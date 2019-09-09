#!/bin/bash

set -euo pipefail

VCPUS=4
worker_iam_policy_file="iam/policy-templates/${APP_NAME}-lambda.json"
worker_iam_policy="${APP_NAME}-etl-worker"
ENSURE_POLICY="import sys, json; from aegea.util.aws import ensure_iam_role, IAMPolicyBuilder as pb; ensure_iam_role('$worker_iam_policy', policies=[pb(json.load(sys.stdin))], trust=['batch'])"
cat "$worker_iam_policy_file" | envsubst | python -c "$ENSURE_POLICY"
aegea batch submit --job-role $worker_iam_policy --mount-instance-storage --vcpus $VCPUS --execute ${APP_HOME}/scripts/etl.sh --environment STAGE=$STAGE SERVICE_S3_BUCKET=$SERVICE_S3_BUCKET --watch