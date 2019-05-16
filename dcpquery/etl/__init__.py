import os, re, json, tempfile
from collections import OrderedDict

from dcplib.etl import DSSExtractor
from hca.dss import DSSClient

from .. import config
from ..db import Bundle, File, BundleFileLink, ProcessFileLink, Process, ProcessProcessLink, DCPMetadataSchemaType


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
            if f == fm["name"]:
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


def get_file_extension(filename):
    try:
        regex_search_result = re.search('^(?:(?:.){1,}?)((?:[.][a-z]{1,10}){1,2})$', filename)
        file_extension = regex_search_result.group(1)
    except AttributeError:
        file_extension = None
    return file_extension


class BundleLoader:
    def __init__(self):
        schema_types = config.db_session.query(DCPMetadataSchemaType).with_entities(DCPMetadataSchemaType.name).all()
        self.schema_types = [schema[0] for schema in schema_types]

    def register_dcp_metadata_schema_type(self, schema_type):
        if schema_type and schema_type not in self.schema_types:
            schema = DCPMetadataSchemaType(name=schema_type)
            config.db_session.add(schema)
            config.db_session.commit()
            self.schema_types.append(schema_type)

    def load_bundle(self, bundle, extractor=None, transformer=None):
        bf_links = []
        bundle_row = Bundle(uuid=bundle["uuid"], version=bundle["version"], manifest=bundle["manifest"])
        for file_data in bundle["files"]:
            filename = file_data.pop("name")
            file_extension = get_file_extension(filename)

            if filename == "links.json":
                links = file_data['body']['links']
                load_links(links)

            self.register_dcp_metadata_schema_type(file_data['schema_type'])
            file_row = File(
                uuid=file_data['uuid'],
                version=file_data['version'],
                content_type=file_data['content-type'],
                size=file_data['size'],
                extension=str(file_extension),
                body=file_data['body'],
                dcp_schema_type_name=file_data['schema_type']
            )

            bf_links.append(BundleFileLink(bundle=bundle_row, file=file_row, name=filename))
        config.db_session.add_all(bf_links)
        config.db_session.commit()


def create_view_tables(extractor):
    schema_types = [schema[0] for schema in
                    config.db_session.query(DCPMetadataSchemaType).with_entities(DCPMetadataSchemaType.name).all()]
    for schema_type in schema_types:
        config.db_session.execute(
            f"""
              CREATE OR REPLACE VIEW {schema_type} AS
              SELECT f.* FROM files as f
              WHERE f.dcp_schema_type_name = '{schema_type}'
            """
        )
    config.db_session.commit()


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
        children = children + [child[0] for child in child_uuids]
    return list(set(children))


def get_parent_process_uuids(input_file_uuids):
    parents = []
    for file_uuid in input_file_uuids:
        parent_uuids = config.db_session.query(ProcessFileLink).with_entities(ProcessFileLink.process_uuid).filter(
            ProcessFileLink.file_uuid == file_uuid,
            ProcessFileLink.process_file_connection_type == 'OUTPUT_ENTITY'
        ).all()

        parents = parents + [parent[0] for parent in parent_uuids]
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


def etl_one_bundle(bundle_uuid, bundle_version):
    dss_client = DSSClient(swagger_url=f"https://{os.environ['DSS_HOST']}/v1/swagger.json")
    extractor = DSSExtractor(staging_directory=tempfile.gettempdir(), dss_client=dss_client)
    print(extractor.get_files_to_fetch_for_bundle(bundle_uuid=bundle_uuid, bundle_version=bundle_version))
    # TODO: (akislyuk): implement etl_one_bundle
