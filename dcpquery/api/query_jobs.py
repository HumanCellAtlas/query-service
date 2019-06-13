import os, sys, json

import botocore, requests
from dcplib import aws
from flask import Response
from urllib.parse import urlencode
from dcplib.aws import clients, resources

from dcpquery.db import run_query
from dcpquery.exceptions import DCPQueryError
from .. import config
from . import JSONEncoder


def get(job_id, redirect_when_waiting=False, redirect_when_done=False):
    bucket = resources.s3.Bucket(config.s3_bucket_name)
    job_status_object = bucket.Object(f"job_status/{job_id}")
    try:
        job_status_object.load()
        job_status = json.load(job_status_object.get()["Body"])
    except botocore.exceptions.ClientError as e:
        if "Not Found" in str(e):
            return Response(status=requests.codes.not_found, response=b"{}")
        raise
    if job_status["status"] in {"new", "running"} and redirect_when_waiting:
        return Response(status=requests.codes.moved,
                        headers={"Location": job_id + "?" + urlencode(config.app.current_request.query_params),
                                 "Retry-After": "60",
                                 "Content-Type": "application/json"},
                        response=json.dumps(job_status).encode())
    if job_status.get("result_location") is not None:
        result_url = clients.s3.generate_presigned_url(ClientMethod="get_object",
                                                       Params=dict(**job_status["result_location"]),
                                                       ExpiresIn=60 * 60 * 24 * 7)
        job_status["result_url"] = result_url
        if redirect_when_done:
            return Response(status=requests.codes.found,
                            headers={"Location": result_url, "Content-Type": "application/json"},
                            response=json.dumps(job_status).encode())
    return job_status


def set_job_status(job_id, status, error=None, result_location=None):
    bucket = aws.resources.s3.Bucket(config.s3_bucket_name)
    job_status_object = bucket.Object(f"job_status/{job_id}")
    job_status_doc = {"job_id": job_id, "status": status, "error": error, "result_location": result_location}
    job_status_object.put(Body=json.dumps(job_status_doc, cls=JSONEncoder).encode())
    return {"Bucket": bucket.name, "Key": job_status_object.key}


def set_job_result(job_id, query, params, result, error=None):
    bucket = aws.resources.s3.Bucket(config.s3_bucket_name)
    job_result_object = bucket.Object(f"job_result/{job_id}")
    job_result_doc = dict(job_id=job_id, status="done", query=query, params=params, result=result, error=error)
    job_result_object.put(Body=json.dumps(job_result_doc, cls=JSONEncoder).encode())
    return {"Bucket": bucket.name, "Key": job_result_object.key}


def process_async_query(event_record):
    job_id = event_record["messageId"]
    set_job_status(job_id, status="running")
    event = json.loads(event_record["body"])
    query, params = event["query"], event["params"]
    try:
        results = []
        total_result_size = 0
        config.reset_db_timeout_seconds(880)
        for result in run_query(query, params):
            total_result_size += len(json.dumps(result, cls=JSONEncoder))
            results.append(result)
            if total_result_size > config.S3_SINGLE_UPLOAD_MAX_SIZE:
                # TODO stream large query results to s3
                break
        job_result_location = set_job_result(job_id, query=query, params=params, result=results)
        set_job_status(job_id, status="done", result_location=job_result_location)
    except DCPQueryError as e:
        set_job_status(job_id, status="failed", error=e.to_problem().body)
    except Exception as e:
        problem = DCPQueryError(status=500, title="Async query internal error", detail=str(e)).to_problem().body
        set_job_status(job_id, status="failed", error=problem)
