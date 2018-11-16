import json

import requests

from query.lib.common.logging import get_logger
from query.lib.config import Config
from query.lib.db.database import PostgresDatabase
from .. import return_exceptions_as_http_errors

logger = get_logger('query.lambdas.api_server.v1.fast_query')

db = PostgresDatabase(Config.serve_database_uri)


@return_exceptions_as_http_errors
def query(query_string):
    query_string = json.loads(query_string, strict=False)
    query_results = db.run_read_only_query(query_string)
    return {'query': query_string, "results": query_results}, requests.codes.ok
