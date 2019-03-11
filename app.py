import os, sys, json

import boto3, requests, sqlalchemy
from requests_http_signature import HTTPSignatureAuth
from chalice import Chalice, Response
from dcplib.etl import DSSExtractor

from dcpquery import api, config, aws
from dcpquery.db import run_query
from dcpquery.exceptions import DCPQueryError

swagger_spec_path = os.path.join(os.path.dirname(__file__), f'{os.environ["APP_NAME"]}-api.yml')
app = api.DCPQueryServer(app_name=os.environ["APP_NAME"], swagger_spec_path=swagger_spec_path)
config.app = app


@app.route("/")
def root():
    body = f'<html><body>Hello from {os.environ["APP_NAME"]}! Swagger UI is <a href="/ui">here</a>.</body></html>'
    return Response(status_code=requests.codes.ok, headers={"Content-Type": "text/html"}, body=body)


@app.route("/internal/health")
def health_check():
    return json.dumps({"db": str(app.db)})


@app.route("/bundles/event", methods=["POST"])
def handle_bundle_event():
    print("Received bundle event:")
    print(app.current_request.json_body)
    HTTPSignatureAuth.verify(requests.Request(url="http://host/bundles/event",
                                              method=app.current_request.method,
                                              headers=app.current_request.headers),
                             key_resolver=lambda key_id, algorithm: config.webhook_keys[key_id].encode())
    aws.send_sqs_message(queue_name=config.bundle_events_queue_name, message=app.current_request.json_body)


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
