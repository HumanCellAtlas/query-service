import requests, sqlalchemy
from flask import redirect

from .. import config
from ..exceptions import DCPQueryError, QueryTimeoutError
from ..db import run_query
from .query_job import create_async_query_job


def post(body):
    query = body["query"]
    # FIXME: make sure tests include readonly enforcement
    try:
        result = run_query(query).fetchall()
    except QueryTimeoutError:
        job_id = create_async_query_job(query)
        return redirect(f"query_jobs/{job_id}")
    return {"query": query, "result": result}, requests.codes.ok
