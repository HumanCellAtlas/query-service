import json

from query.lambdas.load_data.load_data import extract_transform_load
from query.lib.common.logging import get_logger
from query.lib.config import Config
from query.lib.db.database import PostgresDatabase
from query.lib.etl.extract import S3Extractor
from query.lib.etl.load import PostgresLoader
from query.lib.etl.s3_client import S3Client

logger = get_logger(__name__)

# TODO: don't hardcode to staging, don't read directly from s3
extractor = S3Extractor(S3Client('us-east-1', 'org-hca-dss-staging'))
loader = PostgresLoader(PostgresDatabase(Config.serve_database_uri))


def load_data(event, context):
    bundle_info = json.loads(event['Records'][0]['body'])
    extract_transform_load(
        extractor=extractor,
        loader=loader,
        bundle_uuid=bundle_info['bundle_uuid'],
        bundle_version=bundle_info['bundle_version']
    )