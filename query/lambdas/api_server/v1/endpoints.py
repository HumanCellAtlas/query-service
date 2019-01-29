import json
from uuid import uuid4

import boto3
import requests

from query.lib.common.formatting import format_query_results
from query.lib.common.logging import get_logger
from query.lib.config import Config
from query.lib.db.database import PostgresDatabase
from query.lambdas.api_server import return_exceptions_as_http_errors

logger = get_logger('query.lambdas.api_server.v1.endpoints')

db = PostgresDatabase(Config.serve_database_uri)
sqs_client = boto3.client('sqs')
s3_client = boto3.client('s3')


@return_exceptions_as_http_errors
def health():
    return requests.codes.ok


@return_exceptions_as_http_errors
def query(query_string):
    query_string = json.loads(query_string, strict=False)
    query_results, column_names = db.run_read_only_query(query_string)
    formatted_query_results = format_query_results(query_results, column_names)
    return {'query': query_string, "results": formatted_query_results}, requests.codes.ok


@return_exceptions_as_http_errors
def create_async_query(query_string):
    query_string = json.loads(query_string, strict=False)
    uuid = uuid4()
    with db.transaction() as (_, tables):
        tables.job_status.insert(uuid)
    sqs_client.send_message(
        QueueUrl=Config.async_query_queue_url,
        MessageBody=json.dumps({'query': query_string, 'job_id': str(uuid)})
    )
    return {'query': query_string, 'job_id': str(uuid)}, requests.codes.accepted


@return_exceptions_as_http_errors
def get_async_query_job_status(job_id):
    with db.transaction() as (_, tables):
        job = tables.job_status.select(job_id)
        if job is None:
            return {'job_id': job_id, 'status': 'Not Found'}, requests.codes.not_found
    status = job['status']
    if status == "COMPLETE":
        presigned_url = _gen_presigned_url(job_id)
        return {'job_id': job_id, 'status': status, 'presigned_url': presigned_url}, requests.codes.ok
    return {'job_id': job_id, 'status': status}, requests.codes.ok


@return_exceptions_as_http_errors
def webhook(subscription_data):
    subscription_data = json.loads(subscription_data, strict=False)
    response = sqs_client.send_message(
        QueueUrl=Config.load_data_queue_url,
        MessageBody=json.dumps(subscription_data['match'])
    )
    return {'response': response}, requests.codes.accepted


def _gen_presigned_url(job_id):
    deployment_stage = Config.deployment_stage
    presigned_url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params=dict(Bucket=Config.query_service_bucket, Key=f"{deployment_stage}/query_results/{job_id}")
    )
    return presigned_url
