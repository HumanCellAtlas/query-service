"""
This module provides access to administrative commands for the DCP Query Service database.
"""

import os, sys, argparse, logging, json, re
from collections import defaultdict

from dcplib.etl import DSSExtractor
from dcpquery.db import Bundle, File, BundleFileLink

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
elif args.action in {"load", "load-test"}:
    if args.action == "load":
        extractor_args = {}  # type: ignore
    else:
        extractor_args = {"query": {"query": {"match": {"uuid": "000f989a-bea2-46cb-9ec1-b4de8c292931"}}}}

    def tf(bundle_uuid, bundle_version, bundle_path, bundle_manifest_path, extractor):
        result = dict(uuid=bundle_uuid,
                      version=bundle_version,
                      manifest=json.load(open(bundle_manifest_path)),
                      aggregate_metadata=defaultdict(list),
                      files=[])
        for f in os.listdir(bundle_path):
            if re.match(r"(.+)_(\d+).json", f):
                metadata_key, index = re.match(r"(.+)_(\d+).json", f).groups()
            elif re.match(r"(.+).json", f):
                metadata_key, index = re.match(r"(.+).json", f).group(1), None
            else:
                metadata_key, index = f, None
            with open(os.path.join(bundle_path, f)) as fh:
                file_doc = json.load(fh)
                if index is None:
                    result["aggregate_metadata"][metadata_key] = file_doc
                else:
                    result["aggregate_metadata"][metadata_key].append(file_doc)
            for fm in result["manifest"]["files"]:
                if f == fm["name"]:
                    result["files"].append(dict(uuid=fm["uuid"],
                                                version=fm["version"],
                                                body=file_doc,
                                                content_type=fm["content-type"],
                                                name=fm["name"],
                                                size=fm["size"]))
        return result

    def ld(bundle, extractor, transformer):
        bundle_row = Bundle(uuid=bundle["uuid"], version=bundle["version"], manifest=bundle["manifest"])
        bf_links = []

        for f in bundle["files"]:
            filename = f.pop("name")
            file_row = File(**f)
            bf_links.append(BundleFileLink(bundle=bundle_row, file=file_row, name=filename))

        config.db_session.add_all(bf_links)
        config.db_session.commit()

    DSSExtractor(staging_directory=".").extract(transformer=tf, loader=ld, **extractor_args)
elif args.action == "connect":
    os.execvp("psql", ["psql", str(config.db.url).replace("postgresql+psycopg2://", "postgres://")])
