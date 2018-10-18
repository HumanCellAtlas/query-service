#!/usr/bin/env python3
import re
import sys

from hca import HCAConfig
from hca.dss import DSSClient

from lib.config import Config
from lib.database import PostgresDatabase
from lib.load import PostgresLoader
from lib.logger import logger
from lib.model import Bundle
from lib.extract import DSSClientExtractor


db = PostgresDatabase(Config.serve_database_uri)
loader = PostgresLoader(db)

uuid_regexp = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.IGNORECASE)

hca_config = HCAConfig()
# hca_config['DSSClient'].swagger_url = f"https://dss.{Config.deployment_stage}.data.humancellatlas.org/v1/swagger.json"
hca_config['DSSClient'].swagger_url = f"https://dss.staging.data.humancellatlas.org/v1/swagger.json"

dss = DSSClient(config=hca_config)
extractor = DSSClientExtractor(dss)

if __name__ == '__main__':

    for line in sys.stdin:
        bundle_uuid, bundle_version = line.strip().split('.', 1)

        if not uuid_regexp.match(bundle_uuid):
            logger.warn(f"Not a valid UUID: \"{bundle_uuid}\"")
            continue

        try:
            bundle = Bundle.from_extractor(extractor, bundle_uuid, bundle_version)
            loader.load(bundle)
            logger.info(f"Completed ETL for bundle: \"{bundle_uuid}\"")
        except Exception as e:
            logger.exception(f"Could not load bundle with uuid: \"{bundle_uuid}\"")
            # raise e
