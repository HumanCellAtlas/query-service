import json

from query.lambdas.long_query.create_long_query import query_db_and_put_results_in_s3
from query.lib.common.logging import get_logger

logger = get_logger(__name__)


def create_long_query(event, context):
    job_info = json.loads(event['Records'][0]['body'])
    query_db_and_put_results_in_s3(job_info['job_id'], job_info['query'])

