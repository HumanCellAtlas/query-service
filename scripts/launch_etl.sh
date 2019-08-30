#!/bin/bash

set -euo pipefail

aegea ecs run --fargate-cpu "4 vCPU" --fargate-memory 16GB --execute ${APP_HOME}/scripts/etl.sh --environment STAGE=$STAGE SERVICE_S3_BUCKET=$SERVICE_S3_BUCKET
