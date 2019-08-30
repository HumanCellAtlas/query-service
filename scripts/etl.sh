#!/bin/bash

set -eo pipefail

cd /mnt

export AWS_DEFAULT_REGION=us-east-1 DEBIAN_FRONTEND=noninteractive LC_ALL=C.UTF-8 LANG=C.UTF-8
source /etc/profile

apt-get install --yes jq moreutils gettext make virtualenv zip unzip httpie git

virtualenv --python=python3 .venv
source .venv/bin/activate
[[ -d query-service/.git ]] || git clone --depth 1 https://github.com/HumanCellAtlas/query-service.git
cd query-service
pip install --quiet -r requirements-dev.txt

source environment
S3_CACHE_URL=s3://${SERVICE_S3_BUCKET}/etl/cache.xz
aws s3 cp $S3_CACHE_URL - | tar -xJ
scripts/db_ctl load --db remote
# TODO: ETL cache should have a facility for purging deleted metadata
tar -cJ bundle_manifests bundles files | aws s3 cp - $S3_CACHE_URL
