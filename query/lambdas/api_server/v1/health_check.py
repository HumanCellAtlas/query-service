import requests

from .. import return_exceptions_as_http_errors


@return_exceptions_as_http_errors
def health():
    return requests.codes.ok
