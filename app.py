import os, sys, json

import boto3, requests, sqlalchemy, jinja2
from requests_http_signature import HTTPSignatureAuth
from chalice import Chalice, Response
from dcplib import aws

import dcpquery
from dcpquery import api, ui, config
from dcpquery.api.query_jobs import process_async_query, set_job_status
from dcpquery.etl import process_bundle_event

swagger_spec_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), f'{os.environ["APP_NAME"]}-api.yml')
app = api.DCPQueryServer(app_name=os.environ["APP_NAME"], swagger_spec_path=swagger_spec_path)
config.app = app
config.configure_logging()


@app.route("/")
def root():
    with open(os.path.join(os.path.abspath(os.path.dirname(dcpquery.__file__)), "ui", "index.html")) as fh:
        body = jinja2.Template(fh.read()).render(env=os.environ)
    return Response(status_code=requests.codes.ok, headers={"Content-Type": "text/html"}, body=body)


@app.route("/internal/health")
def serve_health_check():
    config.db_session.execute("SELECT 1")
    list(aws.resources.s3.Bucket(config.s3_bucket_name).objects.limit(1))
    return {"status": "OK", "version_info": {"version": os.environ.get("VERSION")}}


@app.route("/version")
def serve_version():
    return {"version_info": {"version": os.environ.get("VERSION")}}


@app.route("/bundles/event", methods=["POST"])
def receive_bundle_event():
    app.log.info("Received bundle event: %s", app.current_request.json_body)
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
        app.log.info("Processing bundle event:", record.body)
        process_bundle_event(json.loads(record.body))


@app.on_sqs_message(queue=config.async_queries_queue_name)
def async_query_handler(event):
    for record in event:
        process_async_query(record.to_dict())
