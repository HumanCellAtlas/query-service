"""
This module provides access to administrative commands for the DCP Query Service database.
"""

import os, sys, argparse, logging

from .. import config
from . import init_database

logging.basicConfig(level=logging.INFO)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("action", choices={"init", "load", "load-test", "connect"})
parser.add_argument("--db", choices={"local", "remote"}, default="local")
parser.add_argument("--dry-run", action="store_true", help="Print commands that would be executed without running them")
args = parser.parse_args(sys.argv[1:])

if args.db == "remote":
    config.local_mode = False

if args.action == "init":
    init_database(**vars(args))
elif args.action == "load":
    raise NotImplementedError()
elif args.action == "load-test":
    raise NotImplementedError()
elif args.action == "connect":
    os.execvp("psql", ["psql", str(config.db.url).replace("postgresql+psycopg2://", "postgres://")])
