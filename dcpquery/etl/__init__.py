import os, sys, re, json
from collections import defaultdict

from .. import config
from ..db import Bundle, File, BundleFileLink


def transform_bundle(bundle_uuid, bundle_version, bundle_path, bundle_manifest_path, extractor):
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


def load_bundle(bundle, extractor, transformer):
    bundle_row = Bundle(uuid=bundle["uuid"], version=bundle["version"], manifest=bundle["manifest"])
    bf_links = []

    for f in bundle["files"]:
        filename = f.pop("name")
        file_row = File(**f)
        bf_links.append(BundleFileLink(bundle=bundle_row, file=file_row, name=filename))

    config.db_session.add_all(bf_links)
    config.db_session.commit()
