#!/usr/bin/env python3
import re
import sys
import typing
from multiprocessing import Pool

from hca import HCAConfig
from hca.dss import DSSClient

from lib.config import Config
from lib.database import PostgresDatabase
from lib.load import PostgresLoader, Loader
from lib.logger import logger
from lib.model import Bundle
from lib.extract import DSSClientExtractor, Extractor

# this seems to be entirely IO bound, so we can have _lots_ of workers...
CONCURRENCY = 50

BUNDLE_FQID_REGEXP = re.compile(
    '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}[.][0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{6}[.][0-9]{6}Z$',
    re.IGNORECASE
)


def chunks(seq, size):
    return (seq[i::size] for i in range(size))


def extract_transform_load(extractor: Extractor, loader: Loader, bundle_fqid: str):
    if not BUNDLE_FQID_REGEXP.match(bundle_fqid):
        logger.warn(f"Not a valid bundle FQID: \"{bundle_fqid}\"")
        return
    try:
        bundle_uuid, bundle_version = bundle_fqid.split('.', 1)
        bundle = Bundle.from_extractor(extractor, bundle_uuid, bundle_version)
        loader.load(bundle)
        logger.info(f"Completed ETL for bundle: \"{bundle_uuid}\"")
    except:
        logger.exception(f"Could not load bundle with uuid: \"{bundle_uuid}\"")


def process_batch(batch: typing.List[str]):
    config = HCAConfig()
    # TODO: don't hardcode to staging
    config['DSSClient'].swagger_url = f"https://dss.staging.data.humancellatlas.org/v1/swagger.json"
    loader = PostgresLoader(PostgresDatabase(Config.serve_database_uri))
    extractor = DSSClientExtractor(DSSClient(config=config))
    for bundle_fqid in batch:
        extract_transform_load(extractor, loader, bundle_fqid)


if __name__ == '__main__':
    bundle_fqids = []
    for line in sys.stdin:
        bundle_fqids.append(line.strip())
    with Pool(CONCURRENCY) as p:
        bundle_fqid_chunks = chunks(bundle_fqids, CONCURRENCY)
        p.map(process_batch, bundle_fqid_chunks)

