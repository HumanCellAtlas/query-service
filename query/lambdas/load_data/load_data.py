import json

from query.lib.etl.transform import BundleDocumentTransform
from query.lib.config import Config
from query.lib.db.database import PostgresDatabase
from query.lib.etl.extract import S3Extractor, Extractor
from query.lib.etl.load import PostgresLoader, Loader
from query.lib.etl.s3_client import S3Client
from query.lib.common.logging import get_logger

logger = get_logger('query.lambdas.load_data.load_data')

# TODO: don't hardcode to staging, don't read directly from s3
extractor = S3Extractor(S3Client('us-east-1', 'org-hca-dss-staging'))
loader = PostgresLoader(PostgresDatabase(Config.serve_database_uri))


class LoadData:
    def query_service_data_load(self, event, context):
        bundle_info = json.loads(event['Records'][0]['body'])
        self.extract_transform_load(
            extractor=extractor,
            loader=loader,
            bundle_uuid=bundle_info['bundle_uuid'],
            bundle_version=bundle_info['bundle_version']
        )

    def extract_transform_load(self, extractor: Extractor, loader: Loader, bundle_uuid: str, bundle_version: str):
        try:
            bundle = extractor.extract_bundle(bundle_uuid, bundle_version)
            transformed_bundle = BundleDocumentTransform.transform(bundle)
            loader.load(bundle, transformed_bundle)
            logger.info(f"Completed ETL for bundle with FQID: \"{bundle_uuid}.{bundle_version}\"")
        except Exception as e:
            logger.info(f"Could not load bundle with FQID: \"{bundle_uuid}.{bundle_version}\", EXCEPTION: {e}")
