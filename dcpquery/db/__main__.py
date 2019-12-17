"""
This module provides access to administrative commands for the DCP Query Service database.
"""

import os, sys, argparse, logging, json

from hca.dss import DSSClient
from dcplib.etl import DSSExtractor

from .. import config
from ..etl import dcpquery_etl_finalizer, etl_bundles
from dcpquery.db import commit_to_db
from dcpquery.etl import transform_bundle

from . import init_db, drop_db, migrate_db

fmi_test_query = {
    "query": {
        "match": {
            "files.project_json.project_core.project_short_name": "Fetal/Maternal Interface"
        }
    }
}

hpsi_test_query = {
    "query": {
        "match": {
            "files.project_json.project_core.project_short_name": "Tissue stability"
        }
    }
}

default_test_query = {
    "query": {
        "match": {
            "files.project_json.project_core.project_short_name": "Tissue stability"
        }
    }
}

config.configure_logging()
common_opts_parser = argparse.ArgumentParser(add_help=False)
common_opts_parser.add_argument("--db", choices={"local", "remote"}, default="local")
common_opts_parser.add_argument("--dss-swagger-url", default=f"https://{config.dss_host}/v1/swagger.json")
common_opts_parser.add_argument("--dry-run", action="store_true",
                                help="Print commands that would be executed without running them")
common_opts_parser.add_argument("--test-query", type=json.loads, default=default_test_query)
parser = argparse.ArgumentParser(description=__doc__, prog="db_ctl")
subparsers = parser.add_subparsers(dest="command")
subparsers.add_parser("init", help="Initialize database table schema and rules", parents=[common_opts_parser])
subparsers.add_parser("drop", help="Drop database (destroys data)", parents=[common_opts_parser])
subparsers.add_parser("load", help="Load all metadata from data store (runs ETL)", parents=[common_opts_parser])
subparsers.add_parser("load-test", help="Load metadata test set from DSS (runs ETL)", parents=[common_opts_parser])
subparsers.add_parser("connect", help="Connect to the database and open interactive psql shell",
                      parents=[common_opts_parser])
subparsers.add_parser("describe", help="Connect to the database and describe vital statistics",
                      parents=[common_opts_parser])
run_parser = subparsers.add_parser("run", help="Connect to the database and run specified command",
                                   parents=[common_opts_parser])
run_parser.add_argument("commands", nargs=argparse.REMAINDER)
subparsers.add_parser("migrate", help="Migrate database schema to the latest version", parents=[common_opts_parser])
alembic_parser = subparsers.add_parser("alembic", help="Run the Alembic SQLAlchemy migration manager CLI")
alembic_parser.add_argument("alembic_args", nargs=argparse.REMAINDER)


def print_alembic_help():
    import alembic.config
    return alembic.config.CommandLine("db_ctl alembic").parser.print_help()


alembic_parser.print_help = print_alembic_help  # type: ignore

args = parser.parse_args(sys.argv[1:])
if args.command is None:
    parser.print_help()
    exit()

if args.db == "remote":
    config.local_mode = False
if not args.dry_run:
    config.readonly_db = False

if args.command == "alembic":
    from alembic.config import CommandLine
    alembic_cli = CommandLine("db_ctl")
    alembic_opts = alembic_cli.parser.parse_args(args.alembic_args)
    if not hasattr(alembic_opts, "cmd"):
        exit(alembic_cli.parser.print_help())
    exit(alembic_cli.run_cmd(config.alembic_config, alembic_opts))
elif args.command == "init":
    init_db(dry_run=args.dry_run)
elif args.command == "drop":
    drop_db(dry_run=args.dry_run)
elif args.command == "migrate":
    migrate_db()
elif args.command in {"load", "load-test"}:
    test = False
    if args.command == "load-test":
        test=True
    etl_bundles(test=test)
elif args.command in {"connect", "run", "describe"}:
    db_url = str(config.db.url).replace("postgresql+psycopg2://", "postgres://")
    print(f"Connecting to {db_url}")
    psql_args = ["psql", db_url]
    if args.command == "run":
        for command in args.commands:
            psql_args.extend(["--command", command])
    elif args.command == "describe":
        psql_args.extend(["--command", r"\d+"])
    if args.dry_run:
        print("psql", psql_args)
    else:
        os.execvp("psql", psql_args)
