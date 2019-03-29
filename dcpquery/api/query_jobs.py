import os, sys, json
import botocore, requests
from flask import Response
from urllib.parse import urlencode
from dcplib.aws import clients, resources

from .. import config


def get(job_id, redirect_when_waiting=False, redirect_when_done=False):
    bucket = resources.s3.Bucket(config.s3_bucket_name)
    job_status_object = bucket.Object(f"job_status/{job_id}")
    try:
        job_status_object.load()
        job_status = json.load(job_status_object.get()["Body"])
    except botocore.exceptions.ClientError as e:
        if "Not Found" in str(e):
            return Response(status=requests.codes.not_found,
                            response=json.dumps({}).encode())
    if job_status["status"] in {"new", "running"} and redirect_when_waiting:
        return Response(status=requests.codes.moved,
                        headers={"Location": job_id + "?" + urlencode(config.app.current_request.query_params),
                                 "Retry-After": "60",
                                 "Content-Type": "application/json"},
                        response=json.dumps(job_status).encode())
    if "result_location" in job_status:
        result_url = resources.s3.generate_presigned_url(ClientMethod="GetObject",
                                                         Params=dict(**job_status["result_location"]),
                                                         ExpiresIn=60 * 60 * 24 * 7)
        job_status["result_url"] = result_url
        if redirect_when_done:
            return Response(status=requests.codes.found,
                            headers={"Location": result_url, "Content-Type": "application/json"},
                            response=json.dumps(job_status).encode())
    return job_status
