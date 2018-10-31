import json

import requests

from query.lib.common.logging import get_logger
from .. import return_exceptions_as_http_errors

logger = get_logger('query.lambdas.api_server.v1.fast_query')


@return_exceptions_as_http_errors
def query(query_string):
    query_string = json.loads(query_string)
    logger.info(query_string)
    return {'query': query_string}, requests.codes.ok
