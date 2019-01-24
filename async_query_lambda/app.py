import json

from query.lambdas.async_query.create_async_query import process_async_query
from query.lib.common.logging import get_logger

logger = get_logger(__name__)


def handler(event, context):
    job_info = json.loads(event['Records'][0]['body'])
    process_async_query(job_info['job_id'], job_info['query'])

