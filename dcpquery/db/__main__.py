"""
This module provides access to administrative commands for the DCP Query Service database.
"""

import os, sys, argparse, logging, json

from dcplib.etl import DSSExtractor

from .. import config
from ..etl import transform_bundle, load_bundle
from . import DCPQueryDBManager

default_test_query = {
    "query": {
        "match": {
            "files.project_json.project_core.project_short_name": "HPSI human cerebral organoids"
        }
    }
}

logging.basicConfig(level=logging.INFO)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("action", choices={"init", "load", "load-test", "connect"})
parser.add_argument("--db", choices={"local", "remote"}, default="local")
parser.add_argument("--dry-run", action="store_true", help="Print commands that would be executed without running them")
parser.add_argument("--test-query", type=json.loads, default=default_test_query)
args = parser.parse_args(sys.argv[1:])

if args.db == "remote":
    config.local_mode = False

if args.action == "init":
    DCPQueryDBManager().init_db(dry_run=args.dry_run)
elif args.action in {"load", "load-test"}:
    if args.action == "load":
        extractor_args = {}  # type: ignore
    else:
        extractor_args = {"query": args.test_query}

    DSSExtractor(staging_directory=".").extract(transformer=transform_bundle, loader=load_bundle, **extractor_args)
elif args.action == "connect":
    os.execvp("psql", ["psql", str(config.db.url).replace("postgresql+psycopg2://", "postgres://")])
