import json

import boto3

from query.lib.common.formatting import format_query_results
from query.lib.config import Config
from query.lib.db.database import PostgresDatabase

db = PostgresDatabase(Config.serve_database_uri)
s3 = boto3.client('s3')


def update_job_status(job_id, status):
    with db.transaction() as (_, tables):
        tables.job_status.update_job_status(job_id, status)


def query_db_and_put_results_in_s3(job_id, query_string):
    update_job_status(job_id, 'PROCESSING')
    try:
        query_results, column_names = db.run_read_only_query(query_string)
        formatted_query_results = format_query_results(query_results, column_names)
        data = json.dumps({"query": query_string, "results": formatted_query_results}, default=str)
        deployment_stage = Config.deployment_stage

        account_id = Config.account_id
        s3.put_object(ACL='authenticated-read',
                      Body=data,
                      Bucket=f"query-service-{account_id}",
                      Key=f"{deployment_stage}/query_results/{job_id}")
        update_job_status(job_id, 'COMPLETE')
    except Exception as e:
        # TODO return any postgres errors back to the user
        update_job_status(job_id, 'FAILED')

