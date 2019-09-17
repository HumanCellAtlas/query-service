#!/usr/bin/env python

"""
trace.py is a general-purpose troubleshooting utility for AWS Lambda based services. When run without arguments, it
prints a troubleshooting guide with links specific to the active application deployment stage.
"""

import os, boto3, subprocess, json

print(__doc__)


def get_logs_commands():
    doc = ""
    log_group_name_prefix = f"/aws/lambda/{os.environ['APP_NAME']}-{os.environ['STAGE']}"
    for log_group in boto3.client("logs").describe_log_groups(logGroupNamePrefix=log_group_name_prefix)["logGroups"]:
        doc += f"    aegea logs --start-time=-5m {log_group['logGroupName']}\n"
    return doc


def get_apigateway_id():
    try:
        tfstate = json.load(open(f".terraform.{os.environ['STAGE']}/remote.tfstate"))
        for resource in tfstate["resources"]:
            if resource["type"] == "aws_api_gateway_deployment":
                return resource["instances"][0]["attributes"]["rest_api_id"]
    except Exception:
        pass


get_logs_doc = get_logs_commands()
region = os.environ['AWS_DEFAULT_REGION']
app_name = os.environ['APP_NAME']
stage = os.environ['STAGE']
app_slug = f"{app_name}-{stage}"
console = "https://console.aws.amazon.com"
print(f"""
Troubleshooting guide

* Get recent AWS Lambda logs on the command line (adjust "-5m" to the appropriate time horizon):

{get_logs_doc}
    * Tip: search for unhandled Python errors and the context around them like this:

    {get_logs_doc.splitlines()[0]} | grep -C 20 Traceback

* Increase logging verbosity of your Lambda code and re-trigger the error, if possible.

    * In Query Service, logging verbosity is governed by `DCPQUERY_DEBUG`.

        * Set DCPQUERY_DEBUG=0 to disable debugging and set the app log level to ERROR.
        * Set DCPQUERY_DEBUG=1 to change the log level to INFO and cause stack traces to appear in error responses.
        * Set DCPQUERY_DEBUG=2 to change the log level to DEBUG and cause stack traces to appear in error responses.

      The default is 1. You can temporarily change the value on deployed functions in the console here:

        * {console}/lambda/home?region={region}#/functions/{app_slug}

* Turn on and examine CloudWatch request logging.

    * Go to {console}/apigateway/home?region={region}#/apis/{get_apigateway_id()}/stages/{stage}
    * Select the "Logs/Tracing" tab
    * Check "Enable CloudWatch Logs", "Enable Detailed CloudWatch Metrics" and "Enable X-Ray Tracing"
    * To see the logs, run:

        aegea logs --start-time=-5m API-Gateway-Execution-Logs_{get_apigateway_id()}/{stage}

    * Turn on and examine X-Ray tracing for the Lambda

        * On {console}/lambda/home?region={region}#/functions/{app_slug},
          select "Active Tracing" under "AWS X-Ray".

        * Go to {console}/xray/home?region={region}#/traces?timeRange=PT1H&filter=service(%22{app_slug}%22)
          to see the traces (for the past hour by default).
""")
