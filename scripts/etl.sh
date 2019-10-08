#!/bin/bash

# This script executes the ETL process. It assumes an Ubuntu Linux environment with superuser privileges.
# It is suitable for running on a stock Ubuntu Docker image using a task scheduler like AWS Batch.
# Use scripts/launch_etl_job.sh to do that.

set -eo pipefail

cd /mnt

export AWS_DEFAULT_REGION=us-east-1 DEBIAN_FRONTEND=noninteractive LC_ALL=C.UTF-8 LANG=C.UTF-8
source /etc/profile

apt-get install -qqy --no-install-suggests --no-install-recommends jq moreutils gettext make virtualenv zip unzip httpie git xz-utils dstat

virtualenv --python=python3 .venv
source .venv/bin/activate
rm -rf query-service
export GIT_DISCOVERY_ACROSS_FILESYSTEM=1
git clone https://github.com/HumanCellAtlas/query-service.git
cd query-service
git checkout dunitz-projects-migration-2
pip install --quiet -r requirements-dev.txt

source environment
#export DSS_HOST='manually set url"
S3_CACHE_URL=s3://${SERVICE_S3_BUCKET}/etl/cache.xz
aws s3 cp $S3_CACHE_URL - | tar -xJ || true
scripts/db_ctl load --db remote
# TODO: ETL cache should have a facility for purging deleted metadata
tar -cJ bundle_manifests bundles files | aws s3 cp - $S3_CACHE_URL
