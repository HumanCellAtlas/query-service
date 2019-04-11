"""
This module provides access to administrative commands for the DCP Query Service database.
"""

import os, sys, argparse, logging

from dcplib.etl import DSSExtractor

from .. import config
from ..etl import transform_bundle, load_bundle
from . import init_database

logging.basicConfig(level=logging.INFO)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("action", choices={"init", "load", "load-test", "connect", "init-test-db"})
parser.add_argument("--db", choices={"local", "remote"}, default="local")
parser.add_argument("--dry-run", action="store_true", help="Print commands that would be executed without running them")
args = parser.parse_args(sys.argv[1:])

# Todo why is this in two places?
if args.db == "remote":
    config.local_mode = False

if args.action in {"init", "init-test-db"}:
    init_database(**vars(args))
elif args.action in {"load", "load-test"}:
    if args.action == "load":
        extractor_args = {}  # type: ignore
    else:
        extractor_args = {"query": {"query": {"match": {"uuid": "ffef2e47-b7d9-4b3f-a1b0-03e7559610ef"}}}}

    DSSExtractor(staging_directory=".").extract(transformer=transform_bundle, loader=load_bundle, **extractor_args)
elif args.action == "connect":
    os.execvp("psql", ["psql", str(config.db.url).replace("postgresql+psycopg2://", "postgres://")])
