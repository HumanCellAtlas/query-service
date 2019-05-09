"""
This module provides access to administrative commands for the DCP Query Service database.
"""

import os, sys, argparse, logging, json

from hca.dss import DSSClient
from dcplib.etl import DSSExtractor

from .. import config
from ..etl import transform_bundle, BundleLoader, create_view_tables

from . import init_db, drop_db

fmi_test_query = {
    "query": {
        "match": {
            "files.project_json.project_core.project_short_name": "Fetal/Maternal Interface"
        }
    }
}

default_test_query = {
    "query": {
        "match": {
            "files.project_json.project_core.project_short_name": "HPSI human cerebral organoids"
        }
    }
}

config.configure_logging()
parser = argparse.ArgumentParser(description=__doc__, prog="db_ctl")
parser.add_argument("action", choices={"init", "drop", "load", "load-test", "connect", "describe", "run"}, nargs="?")
parser.add_argument("commands", nargs="*")
parser.add_argument("--db", choices={"local", "remote"}, default="local")
parser.add_argument("--dss-swagger-url", default=f"https://{config.dss_host}/v1/swagger.json")
parser.add_argument("--dry-run", action="store_true", help="Print commands that would be executed without running them")
parser.add_argument("--test-query", type=json.loads, default=default_test_query)
args = parser.parse_args(sys.argv[1:])

if args.db == "remote":
    config.local_mode = False

if args.action is None:
    parser.print_help()
    parser.exit()

if args.action == "init":
    init_db(dry_run=args.dry_run)
elif args.action == "drop":
    drop_db(dry_run=args.dry_run)
    init_db(dry_run=args.dry_run)
elif args.action in {"load", "load-test"}:
    if args.action == "load":
        extractor_args = {}  # type: ignore
    else:
        extractor_args = {"query": args.test_query}

    dss_client = DSSClient(swagger_url=args.dss_swagger_url)

    DSSExtractor(staging_directory=".").extract(
        transformer=transform_bundle,
        loader=BundleLoader().load_bundle,
        finalizer=create_view_tables,
        **extractor_args
    )
elif args.action in {"connect", "run", "describe"}:
    db_url = str(config.db.url).replace("postgresql+psycopg2://", "postgres://")
    psql_args = ["psql", db_url]
    for command in args.commands:
        psql_args.extend(["--command", command])
    if args.action == "describe":
        psql_args.extend(["--command", r"\d+"])
    os.execvp("psql", psql_args)
