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
            job_status = {"job_id": job_id, "status": "new"}
    if job_status["status"] in {"new", "running"} and redirect_when_waiting:
        return Response(status=requests.codes.moved,
                        headers={"Location": job_id + "?" + urlencode(config.app.current_request.query_params),
                                 "Retry-After": "60",
                                 "Content-Type": "application/json"},
                        response=json.dumps(job_status).encode())
    if "result_location" in job_status:
        result_url = clients.s3.generate_presigned_url(ClientMethod="get_object",
                                                       Params=dict(**job_status["result_location"]),
                                                       ExpiresIn=60 * 60 * 24 * 7)
        job_status["result_url"] = result_url
        if redirect_when_done:
            return Response(status=requests.codes.found,
                            headers={"Location": result_url, "Content-Type": "application/json"},
                            response=json.dumps(job_status).encode())
    return job_status


def process_async_query(job_id, query):
    bucket = aws.resources.s3.Bucket(config.s3_bucket_name)
    job_status_object = bucket.Object(f"job_status/{job_id}")
    job_result_object = bucket.Object(f"job_result/{job_id}")
    try:
        results = []
        total_result_size = 0
        config.reset_db_timeout_seconds(880)
        for result in run_query(query):
            total_result_size += len(json.dumps(result, cls=JSONEncoder))
            results.append(result)
            if total_result_size > config.S3_SINGLE_UPLOAD_MAX_SIZE:
                # TODO stream large query results to s3
                break
        job_result_doc = {"job_id": job_id, "status": "done", "result": results, "error": None}
        job_result_object.put(Body=json.dumps(job_result_doc, cls=JSONEncoder).encode())
        job_status_doc = {"job_id": job_id, "status": "done", "error": None,
                          "result_location": {"Bucket": bucket.name, "Key": job_result_object.key}}
    except DCPQueryError as e:
        job_status_doc = {"job_id": job_id, "status": "done", "error": e.to_problem().body, "result_location": None}
    except Exception as e:
        problem = DCPQueryError(status=500, title="Async query internal error", detail=str(e)).to_problem().body
        job_status_doc = {"job_id": job_id, "status": "done", "error": problem, "result_location": None}

    job_status_object.put(Body=json.dumps(job_status_doc).encode())
