"""
This module provides access to administrative commands for the DCP Query Service database.
"""

import os, sys, argparse, logging

from hca.dss import DSSClient
from dcplib.etl import DSSExtractor

from .. import config
from ..etl import transform_bundle, load_bundle
from . import init_database

logging.basicConfig(level=logging.INFO)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("action", choices={"init", "load", "load-test", "connect"})
parser.add_argument("--db", choices={"local", "remote"}, default="local")
parser.add_argument("--dss-swagger-url", default=f"https://{config.dss_host}/v1/swagger.json")
parser.add_argument("--dry-run", action="store_true", help="Print commands that would be executed without running them")
args = parser.parse_args(sys.argv[1:])

if args.db == "remote":
    config.local_mode = False

if args.action == "init":
    init_database(dry_run=args.dry_run)
elif args.action in {"load", "load-test"}:
    if args.action == "load":
        extractor_args = {}  # type: ignore
    else:
        extractor_args = {"query": {"query": {"match": {"uuid": "000f989a-bea2-46cb-9ec1-b4de8c292931"}}}}

    dss_client = DSSClient(swagger_url=args.dss_swagger_url)
    dss_extractor = DSSExtractor(staging_directory=".", dss_client=dss_client)
    dss_extractor.extract(transformer=transform_bundle, loader=load_bundle, **extractor_args)
elif args.action == "connect":
    os.execvp("psql", ["psql", str(config.db.url).replace("postgresql+psycopg2://", "postgres://")])
