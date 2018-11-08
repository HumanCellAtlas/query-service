import json

import boto3
import requests

from query.lib.common.logging import get_logger
from query.lib.config import Config
from query.lib.db.database import PostgresDatabase
from query.lambdas.api_server import return_exceptions_as_http_errors

logger = get_logger('query.lambdas.api_server.v1.fast_query')

db = PostgresDatabase(Config.serve_database_uri)


@return_exceptions_as_http_errors
def query(query_string):
    query_string = json.loads(query_string, strict=False)
    query_results, column_names = db.run_read_only_query(query_string)
    formatted_query_results = format_query_results(query_results, column_names)
    return {'query': query_string, "results": formatted_query_results}, requests.codes.ok


def format_query_results(query_results, column_names):
    updated_results = []
    for result in query_results:
        new_dict = {k: v for k, v in zip(column_names, result)}
        updated_results.append(new_dict)
    return updated_results


@return_exceptions_as_http_errors
def webhook(new_data):
    new_data = json.loads(new_data)
    client = boto3.client('sqs')
    response = client.send_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/861229788715/dcp-query-data-input-queue-dev',
        MessageBody=new_data
    )

    return {'response': response}, requests.codes.accepted
