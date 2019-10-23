import json
import os
import re
from collections.__init__ import OrderedDict


def transform_bundle(bundle_uuid, bundle_version, bundle_path, bundle_manifest_path, extractor=None):
    """
    This function is used with the ETL interface in dcplib.etl.DSSExtractor.extract.
    Given a bundle ID and directory containing its medatata JSON files, it produces an intermediate representation
    of the bundle and its files ready to be inserted into the database by BundleLoader.
    """
    result = dict(uuid=bundle_uuid,
                  version=bundle_version,
                  manifest=json.load(open(bundle_manifest_path)),
                  aggregate_metadata={},
                  files=OrderedDict())
    # Load and process all the metadata files; construct the "aggregate_metadata" doc:
    # - Singleton metadata files get inserted under their name minus the extension (project.json => {"project": {...}})
    # - Numbered metadata files are put in an array (assay_0.json, assay_1.json => {"assay": [{...0...}, {...1...}]})
    bundle_fetched_files = sorted(os.listdir(bundle_path)) if os.path.exists(bundle_path) else []
    for f in bundle_fetched_files:
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
                result["aggregate_metadata"].setdefault(metadata_key, [])
                result["aggregate_metadata"][metadata_key].append(file_doc)
        for fm in result["manifest"]["files"]:
            if f == fm["name"] and "schema_type" in file_doc:
                result["files"][fm["name"]] = dict(fm,
                                                   body=file_doc,
                                                   schema_type=file_doc['schema_type'])
    # For all other (non-metadata) files from the bundle manifest, insert them with a default body
    # indicating an empty schema type.
    for fm in result["manifest"]["files"]:
        if fm["name"] not in result["files"]:
            result["files"][fm["name"]] = dict(fm,
                                               body=None,
                                               schema_type=None)

    # Flatten the file list while preserving order.
    result["files"] = list(result["files"].values())
    return result
