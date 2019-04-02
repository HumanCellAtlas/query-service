import os, sys, re, json, tempfile
from collections import defaultdict

from hca.dss import DSSClient
from dcplib.etl import DSSExtractor

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


def etl_one_bundle(bundle_uuid, bundle_version):
    dss_client = DSSClient(swagger_url=f"https://{os.environ['DSS_HOST']}/v1/swagger.json")
    extractor = DSSExtractor(staging_directory=tempfile.gettempdir(), dss_client=dss_client)
    os.makedirs(f"{extractor.sd}/files", exist_ok=True)
    os.makedirs(f"{extractor.sd}/bundles", exist_ok=True)
    _, _, files_to_fetch = extractor.get_files_to_fetch_for_bundle(bundle_uuid=bundle_uuid,
                                                                   bundle_version=bundle_version)
    for f in files_to_fetch:
        extractor.get_file(f, bundle_uuid=bundle_uuid, bundle_version=bundle_version)
    extractor.dispatch_callbacks(bundle_uuid=bundle_uuid, bundle_version=bundle_version,
                                 transformer=transform_bundle, loader=load_bundle)
