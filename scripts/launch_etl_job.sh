#!/bin/bash

# This script executes the ETL process in scripts/launch_etl.sh by submitting it as an AWS Batch job.
# Use it to kick off the ETL process after running `source environment` to set the appropriate stage.

set -euo pipefail

worker_iam_policy_file="iam/policy-templates/${APP_NAME}-lambda.json"
worker_iam_policy="${APP_NAME}-${STAGE}-etl-worker"
ENSURE_POLICY="import sys, json; from aegea.util.aws import ensure_iam_role, IAMPolicyBuilder as pb; ensure_iam_role('$worker_iam_policy', policies=[pb(json.load(sys.stdin))], trust=['batch'])"
cat "$worker_iam_policy_file" | envsubst | python -c "$ENSURE_POLICY"
VCPUS=16
MEMORY_MB=16000
aegea batch submit --job-role $worker_iam_policy --mount-instance-storage --vcpus $VCPUS --memory-mb $MEMORY_MB --execute ${APP_HOME}/scripts/etl.sh --environment STAGE=$STAGE --watch
