from uuid import UUID

from query.lib.etl.transform import BundleDocumentTransform
from query.lib.etl.extract import Extractor
from query.lib.etl.load import Loader
from query.lib.common.logging import get_logger

logger = get_logger('query.lambdas.load_data.load_data')


def extract_transform_load(extractor: Extractor, loader: Loader, bundle_uuid: UUID, bundle_version: str):
    bundle = extractor.extract_bundle(bundle_uuid, bundle_version)
    transformed_bundle = BundleDocumentTransform.transform(bundle)
    loader.load(bundle, transformed_bundle)
    logger.info(f"Completed ETL for bundle with FQID: \"{bundle_uuid}.{bundle_version}\"")
