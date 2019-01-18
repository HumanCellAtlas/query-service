import json
import os
from uuid import uuid4

import boto3
import requests

from lib.common.formatting import format_query_results
from query.lib.common.logging import get_logger
from query.lib.config import Config
from query.lib.db.database import PostgresDatabase
from query.lambdas.api_server import return_exceptions_as_http_errors

logger = get_logger('query.lambdas.api_server.v1.endpoints')

db = PostgresDatabase(Config.serve_database_uri)
sqs_client = boto3.client('sqs')


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
def create_long_query(query_string):
    query_string = json.loads(query_string, strict=False)
    uuid = uuid4()
    with db.transaction() as (_, tables):
        tables.job_status.insert(uuid)
    queue_url = Config.long_query_queue_url
    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps({'query': query_string, 'job_id': str(uuid)})
    )
    return {'query': query_string, 'job_id': str(uuid)}, requests.codes.accepted


@return_exceptions_as_http_errors
def get_long_query(job_id):
    with db.transaction() as (_, tables):
        job = tables.job_status.select(job_id)
        if job is None:
            return {'job_id': job_id, 'status': 'Not Found'}, requests.codes.not_found
    status = job['status']
    if status == "COMPLETE":
        s3_url = _format_s3_link(job_id)
        return {'job_id': job_id, 'status': status, 's3_url': s3_url}, requests.codes.ok
    return {'job_id': job_id, 'status': status}, requests.codes.ok


@return_exceptions_as_http_errors
def webhook(subscription_data):
    subscription_data = json.loads(subscription_data, strict=False)
    queue_url = Config.load_data_queue_url
    response = sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(subscription_data['match'])
    )
    return {'response': response}, requests.codes.accepted


def _format_s3_link(job_id):
    account_id = Config.account_id
    deployment_stage = Config.deployment_stage
    return f"https://s3.amazonaws.com/query-service-{account_id}/{deployment_stage}/query_results/{job_id}"
