import json, uuid
import requests

from dcplib import aws

from .. import config


def set_job_status(job_id, status, error=None, result_location=None):
    bucket = aws.resources.s3.Bucket(config.s3_bucket_name)
    job_status_object = bucket.Object(f"job_status/{job_id}")
    job_status_doc = {"job_id": job_id, "status": status, "error": error, "result_location": result_location}
    job_status_object.put(Body=json.dumps(job_status_doc).encode())
    return {"Bucket": bucket.name, "Key": job_status_object.name}


def set_job_result(job_id, result, error=None):
    bucket = aws.resources.s3.Bucket(config.s3_bucket_name)
    job_result_object = bucket.Object(f"job_result/{job_id}")
    job_result_doc = {"job_id": job_id, "status": "done", "result": result, "error": error}
    job_result_object.put(Body=json.dumps(job_result_doc).encode())
    return {"Bucket": bucket.name, "Key": job_result_object.name}


def create_async_query_job(query):
    sqs_receipt = aws.send_sqs_message(queue_name=config.async_queries_queue_name, message=query)
    job_id = sqs_receipt["MessageId"]
    set_job_status(job_id=job_id, status="new")
    return job_id


def post(body):
    query = body["query"]
    job_id = create_async_query_job(query)
    return {"query": query, "job_id": job_id}, requests.codes.accepted
