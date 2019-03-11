import json

import boto3

from query.lib.common.exceptions import DatabaseException
from query.lib.common.formatting import format_query_results
from query.lib.config import Config
from query.lib.db.database import PostgresDatabase
from query.lib.logger import logger

db = PostgresDatabase(Config.serve_database_uri)
s3 = boto3.client('s3')


def update_job_status(job_id, status):
    with db.transaction() as (_, tables):
        tables.job_status.update_job_status(job_id, status)


def process_async_query(job_id, query_string):
    update_job_status(job_id, 'PROCESSING')
    data = query_db(job_id, query_string)
    put_results_in_s3(job_id, data)
    update_job_status(job_id, 'COMPLETE')


def query_db(job_id, query_string):
    try:
        query_results, column_names = db.run_read_only_query(query_string)
        formatted_query_results = format_query_results(query_results, column_names)
        return json.dumps({"query": query_string, "results": formatted_query_results}, default=str)
    except DatabaseException as e:
        # TODO return any postgres errors back to the user
        logger.info(f'Database Error status: {e.status}, details: {e.detail}')
        update_job_status(job_id, 'FAILED')


def put_results_in_s3(job_id, data):
    deployment_stage = Config.deployment_stage
    s3.put_object(ACL='authenticated-read',
                  Body=data,
                  Bucket=Config.query_service_bucket,
                  Key=f"{deployment_stage}/query_results/{job_id}")
