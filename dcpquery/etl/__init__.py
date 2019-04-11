import os, sys, re, json
from collections import defaultdict
from uuid import UUID

import psycopg2
from sqlalchemy.exc import IntegrityError

from .. import config
from ..db import Bundle, File, BundleFileLink, ProcessFileLink, Process, ProcessProcessLink


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
    bf_links = []
    bundle_row = Bundle(uuid=bundle["uuid"], version=bundle["version"], manifest=bundle["manifest"])
    for f in bundle["files"]:
        filename = f.pop("name")
        if filename == "links.json":
            links = f['body']['links']
        file_row = File(**f)
        bf_links.append(BundleFileLink(bundle=bundle_row, file=file_row, name=filename))
    config.db_session.add_all(bf_links)
    config.db_session.commit()
    # Todo is this the best way to avoid race conditions?
    load_links(links)


def load_links(links):
    for link in links:
        process = format_process_info(link)
        process['children'] = get_child_process_uuids(process['output_file_uuids'])
        process['parents'] = get_parent_process_uuids(process['input_file_uuids'])
        create_process(process['process_uuid'])
        create_process_file_links(process)
        link_parent_and_child_processes(process)


def format_process_info(link):
    process_uuid = link['process']
    protocol_uuids = []
    for protocol in link['protocols']:
        protocol_uuid = protocol['protocol_id']
        protocol_uuids.append(protocol_uuid)

    return {"process_uuid": process_uuid, "input_file_uuids": link["inputs"], "output_file_uuids": link["outputs"],
            "protocol_uuids": protocol_uuids}


def get_child_process_uuids(output_file_uuids):
    children = []
    for file_uuid in output_file_uuids:
        child_uuids = config.db_session.query(ProcessFileLink).with_entities(ProcessFileLink.process_uuid).filter(
            ProcessFileLink.file_uuid == file_uuid,
            ProcessFileLink.process_file_connection_type == 'INPUT_ENTITY').all()
        children = children + [c[0] for c in child_uuids]
    return list(set(children))


def get_parent_process_uuids(input_file_uuids):
    parents = []
    for file_uuid in input_file_uuids:
        parent_uuids = config.db_session.query(ProcessFileLink).with_entities(ProcessFileLink.process_uuid).filter(
            ProcessFileLink.file_uuid == file_uuid,
            ProcessFileLink.process_file_connection_type == 'OUTPUT_ENTITY'
        ).all()

        parents = parents + [p[0] for p in parent_uuids]
    return list(set(parents))


def create_process(process_uuid):
    config.db_session.add(Process(process_uuid=process_uuid))
    config.db_session.commit()


def create_process_file_links(process):
    process_file_links = []
    input_file_uuids = process['input_file_uuids']
    output_file_uuids = process['output_file_uuids']
    protocol_uuids = process['protocol_uuids']

    for file_uuid in input_file_uuids:
        process_file_links.append(
            ProcessFileLink(
                process_uuid=process['process_uuid'],
                file_uuid=file_uuid,
                process_file_connection_type='INPUT_ENTITY'
            )
        )

    for file_uuid in output_file_uuids:
        process_file_links.append(
            ProcessFileLink(
                process_uuid=process['process_uuid'],
                file_uuid=file_uuid,
                process_file_connection_type='OUTPUT_ENTITY'
            )
        )

    for file_uuid in protocol_uuids:
        process_file_links.append(
            ProcessFileLink(
                process_uuid=process['process_uuid'],
                file_uuid=file_uuid,
                process_file_connection_type='PROTOCOL_ENTITY'
            )
        )

    config.db_session.add_all(process_file_links)
    config.db_session.commit()


def link_parent_and_child_processes(process):
    process_process_links = []

    already_linked_parents = Process.list_direct_parent_processes(process['process_uuid'])
    already_linked_children = Process.list_direct_child_processes(process['process_uuid'])

    parents = [x for x in process['parents'] if x not in already_linked_parents]
    children = [x for x in process['children'] if x not in already_linked_children]

    for parent in parents:
        process_process_links.append(
            ProcessProcessLink(parent_process_uuid=parent, child_process_uuid=process['process_uuid']))

    for child in children:
        process_process_links.append(
            ProcessProcessLink(parent_process_uuid=process['process_uuid'], child_process_uuid=child))

    config.db_session.add_all(process_process_links)
    config.db_session.commit()
