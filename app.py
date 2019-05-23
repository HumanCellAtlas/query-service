import os, sys, json

import boto3, requests, sqlalchemy
from requests_http_signature import HTTPSignatureAuth
from chalice import Chalice, Response
from dcplib import aws

from dcpquery import api, config
from dcpquery.api.query_jobs import process_async_query, set_job_status
from dcpquery.etl import etl_one_bundle

swagger_spec_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), f'{os.environ["APP_NAME"]}-api.yml')
app = api.DCPQueryServer(app_name=os.environ["APP_NAME"], swagger_spec_path=swagger_spec_path)
config.app = app
config.configure_logging()


@app.route("/")
def root():
    body = f'<html><body>Hello from {os.environ["APP_NAME"]}! Swagger UI is <a href="v1/ui">here</a>.</body></html>'
    return Response(status_code=requests.codes.ok, headers={"Content-Type": "text/html"}, body=body)


@app.route("/internal/health")
def health_check():
    config.db_session.execute("SELECT 1")
    list(aws.resources.s3.Bucket(config.s3_bucket_name).objects.limit(1))
    return {"status": "OK"}


@app.route("/bundles/event", methods=["POST"])
def handle_bundle_event():
    app.log.info("Received bundle event: {}".format(app.current_request.json_body))
    try:
        # The hostname component is ignored in signature calculation
        HTTPSignatureAuth.verify(requests.Request(url="http://host/bundles/event",
                                                  method=app.current_request.method,
                                                  headers=app.current_request.headers),
                                 key_resolver=lambda key_id, algorithm: config.webhook_keys[key_id].encode())
        app.log.info("Authenticated bundle event payload successfully")
        queue_url = aws.clients.sqs.get_queue_url(QueueName=config.bundle_events_queue_name)["QueueUrl"]
        q = aws.resources.sqs.Queue(queue_url)
        res = q.send_message(MessageBody=json.dumps(app.current_request.json_body))
        app.log.info("Forwarded bundle event to %s", queue_url)
    except Exception as e:
        app.log.error("Discarding unauthenticated webhook payload: {}".format(str(e)))
        res = None

    return Response(status_code=requests.codes.accepted, body=res if isinstance(res, dict) else "")


@app.on_sqs_message(queue=config.bundle_events_queue_name)
def bundle_event_handler(event):
    for record in event:
        print("Processing:", record.body)
        dss_event = json.loads(record.body)
        if dss_event["event_type"] != "CREATE":
            continue
        etl_one_bundle(**dss_event["match"])


@app.on_sqs_message(queue=config.async_queries_queue_name)
def async_query_handler(event):
    for record in event:
        process_async_query(record.to_dict())
