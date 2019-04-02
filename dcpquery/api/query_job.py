import json
import uuid
import requests

from dcplib import aws

from .. import config


def create_async_query_job(query):
    q = aws.resources.sqs.Queue(aws.clients.sqs.get_queue_url(QueueName=config.bundle_events_queue_name)["QueueUrl"])
    res = q.send_message(MessageBody=json.dumps(query))
    return res['MessageId']


def post(body):
    query = body["query"]
    job_id = create_async_query_job(query)
    return {"query": query, "job_id": job_id}, requests.codes.accepted
