import uuid
import requests

from dcplib import aws

from .. import config


def create_async_query_job(query):
    sqs_receipt = aws.send_sqs_message(queue_name=config.async_queries_queue_name, message=query)
    return sqs_receipt["MessageId"]


def post(body):
    query = body["query"]
    job_id = create_async_query_job(query)
    return {"query": query, "job_id": job_id}, requests.codes.accepted
