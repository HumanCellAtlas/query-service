import json

import boto3

from query.lambdas.api_server.v1.endpoints import format_query_results
from query.lib.config import Config
from query.lib.db.database import PostgresDatabase

db = PostgresDatabase(Config.serve_database_uri)
s3 = boto3.client('s3')


def query_db_and_put_results_in_s3(job_id, query_string):
    with db.transaction() as (_, tables):
        tables.job_status.update_job_status(job_id, 'PROCESSING')
        try:
            query_results, column_names = db.run_read_only_query(query_string)
            formatted_query_results = format_query_results(query_results, column_names)
            data = json.dumps({"query": query_string, "results": formatted_query_results}, default=str)
            s3.put_object(ACL='public-read',
                          Body=data,
                          Bucket="query-service-861229788715",
                          Key=f"dev/query_results/{job_id}")
            tables.job_status.update_job_status(job_id, 'COMPLETE')
        except:
            # TODO return any postgres errors back to the user
            tables.job_status.update_job_status(job_id, 'FAILED')

