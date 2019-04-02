import os, sys, json

import boto3, requests, sqlalchemy
from requests_http_signature import HTTPSignatureAuth
from chalice import Chalice, Response
from dcplib import aws

from dcpquery import api, config
from dcpquery.db import run_query
from dcpquery.exceptions import DCPQueryError
from dcpquery.etl import etl_one_bundle

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
        app.log.info("Processing:", record.body)
        record = record.body
        if record["event_type"] != "CREATE":
            continue
        etl_one_bundle(**record["match"])


@app.on_sqs_message(queue=config.async_queries_queue_name)
def async_query_handler(event):
    for record in event:
        job_id = record.to_dict()["messageId"]
        bucket = aws.resources.s3.Bucket(config.s3_bucket_name)
        job_status_object = bucket.Object(f"job_status/{job_id}")
        job_result_object = bucket.Object(f"job_result/{job_id}")
        job_status_doc = {"job_id": job_id, "status": "running"}
        job_status_object.put(Body=json.dumps(job_status_doc).encode())
        query = json.loads(record.body)
        try:
            result = run_query(query, timeout_seconds=880).fetchall()
            job_result_doc = {"job_id": job_id, "status": "done", "result": result, "error": None}
            job_result_object.put(Body=json.dumps(job_result_doc).encode())
            job_status_doc = {"job_id": job_id, "status": "done", "error": None,
                              "result_location": {"Bucket": bucket.name, "Key": job_result_object.name}}
            job_status_object.put(Body=json.dumps(job_status_doc).encode())
        except DCPQueryError as e:
            job_status_doc = {"job_id": job_id, "status": "done", "error": e.to_problem.body, "result_location": None}
