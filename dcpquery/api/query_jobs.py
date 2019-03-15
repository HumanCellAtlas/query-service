import os, sys, json
import botocore
from .. import config
from ..aws import clients, resources


def get(job_id):
    bucket = resources.s3.Bucket(config.s3_bucket_name)
    job_status_object = bucket.Object(f"job_status/{job_id}")
    try:
        job_status_object.load()
    except botocore.exceptions.ClientError as e:
        if "Not Found" in str(e):
            return {"job_id": job_id, "status": "new"}
    job_status = json.load(job_status_object.get()["Body"])
    if "result_location" in job_status:
        result_url = resources.s3.generate_presigned_url(ClientMethod="GetObject",
                                                         Params=dict(**job_status["result_location"]),
                                                         ExpiresIn=60 * 60 * 24 * 7)
        job_status["result_url"] = result_url
    return job_status
