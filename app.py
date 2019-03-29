import os, sys, json

import boto3, requests, sqlalchemy
from requests_http_signature import HTTPSignatureAuth
from chalice import Chalice, Response
from dcplib import aws
from dcplib.etl import DSSExtractor

from dcpquery import api, config
from dcpquery.db import run_query
from dcpquery.exceptions import DCPQueryError
from dcpquery.api.query_job import set_job_status, set_job_result

swagger_spec_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), f'{os.environ["APP_NAME"]}-api.yml')
app = api.DCPQueryServer(app_name=os.environ["APP_NAME"], swagger_spec_path=swagger_spec_path)
config.app = app


@app.route("/")
def root():
    body = f'<html><body>Hello from {os.environ["APP_NAME"]}! Swagger UI is <a href="v1/ui">here</a>.</body></html>'
    return Response(status_code=requests.codes.ok, headers={"Content-Type": "text/html"}, body=body)


@app.route("/internal/health")
def health_check():
    return json.dumps({"app": str(app), "db": str(config.db)})


@app.route("/bundles/event", methods=["POST"])
def handle_bundle_event():
    print("Received bundle event:")
    print(app.current_request.json_body)
    try:
        # The hostname component is ignored in signature calculation
        HTTPSignatureAuth.verify(requests.Request(url="http://host/bundles/event",
                                                  method=app.current_request.method,
                                                  headers=app.current_request.headers),
                                 key_resolver=lambda key_id, algorithm: config.webhook_keys[key_id].encode())
    except Exception as e:
        return Response(status_code=requests.codes.forbidden, body=str(e))

    q = aws.resources.sqs.Queue(aws.clients.sqs.get_queue_url(QueueName=config.bundle_events_queue_name)["QueueUrl"])
    res = q.send_message(MessageBody=json.dumps(app.current_request.json_body))
    return Response(status_code=requests.codes.accepted, body=res if isinstance(res, dict) else "")


@app.on_sqs_message(queue=config.bundle_events_queue_name)
def bundle_event_handler(event):
    for record in event:
        print("Processing:", record.body)
        if record["event_type"] != "CREATE":
            continue
        # retrieve bundle using extractor (in-mem?)
        print(DSSExtractor().get_files_to_fetch_for_bundle(**record["match"]))


@app.on_sqs_message(queue=config.async_queries_queue_name)
def async_query_handler(event):
    for record in event:
        job_id = record.to_dict()["messageId"]
        set_job_status(job_id, status="running")
        query = json.loads(record.body)
        try:
            result = run_query(query, timeout_seconds=880).fetchall()
            result_location = set_job_result(job_id, result=result)
            set_job_status(job_id, status="done", result_location=result_location)
        except DCPQueryError as e:
            set_job_status(job_id, status="failed", error=e.to_problem.body)
