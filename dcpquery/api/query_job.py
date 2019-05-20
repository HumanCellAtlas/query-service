import json
import uuid
import requests

from dcplib import aws

from .. import config
from .query_jobs import set_job_status


def create_async_query_job(query):
    q = aws.resources.sqs.Queue(aws.clients.sqs.get_queue_url(QueueName=config.async_queries_queue_name)["QueueUrl"])
    sqs_receipt = q.send_message(MessageBody=json.dumps(query))
    job_id = sqs_receipt["MessageId"]
    set_job_status(job_id=job_id, status="new")
    return job_id


def post(body):
    query = body["query"]
    job_id = create_async_query_job(query)
    return {"query": query, "job_id": job_id}, requests.codes.accepted
