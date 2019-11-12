import logging
import re

from dcpquery import config
from dcpquery.db.models import Bundle, DCPMetadataSchemaType, File, BundleFileLink, Process, ProcessFileLink

logger = logging.getLogger(__name__)


class BundleLoader:
    def __init__(self):
        schema_types = config.db_session.query(DCPMetadataSchemaType).with_entities(DCPMetadataSchemaType.name).all()
        self.schema_types = [schema[0] for schema in schema_types]

    def register_dcp_metadata_schema_type(self, schema_type):
        if schema_type and schema_type not in self.schema_types:
            schema = DCPMetadataSchemaType(name=schema_type)
            config.db_session.add(schema)
            self.schema_types.append(schema_type)

    def load_bundle(self, bundle, extractor=None, transformer=None):
        bf_links = []
        bundle_row = Bundle(uuid=bundle["uuid"],
                            version=bundle["version"],
                            manifest=bundle["manifest"],
                            aggregate_metadata=bundle["aggregate_metadata"])
        for file_data in bundle["files"]:
            filename = file_data.pop("name")
            file_extension = get_file_extension(filename)
            schema_type = None
            major_version = None
            minor_version = None
            if file_data['body']:
                schema_type = file_data['body'].get('describedBy', '').split('/')[-1]
                schema_version = file_data['body'].get('describedBy', '').split('/')[-2]
                major_version = schema_version.split('.')[0]
                minor_version = schema_version.split('.')[1]
            if schema_type == 'links' and file_data["body"]:
                links = file_data['body']['links']
                load_links(links, bundle['uuid'])

            self.register_dcp_metadata_schema_type(schema_type)
            file_row = File(
                uuid=file_data['uuid'],
                version=file_data['version'],
                content_type=file_data['content-type'],
                size=file_data['size'],
                extension=str(file_extension),
                body=file_data['body'],
                dcp_schema_type_name=schema_type,
                schema_major_version=major_version,
                schema_minor_version=minor_version

            )

            bf_links.append(BundleFileLink(bundle=bundle_row, file=file_row, name=filename))
        config.db_session.add_all(bf_links)


def get_file_extension(filename):
    try:
        regex_search_result = re.search('^(?:(?:.){1,}?)((?:[.][a-z]{1,10}){1,2})$', filename)
        file_extension = regex_search_result.group(1)
    except AttributeError:
        file_extension = None
    return file_extension


def load_links(links, bundle_uuid):
    for link in links:
        try:
            process = format_process_info(link)
            config.db_session.add(Process(process_uuid=process['process_uuid']))
            create_process_file_links(process)
        except AssertionError as e:
            logger.error(f"Error while loading link for bundle: {bundle_uuid} error: {e}")


def format_process_info(link):
    assert 'process' in link
    process_uuid = link['process']
    protocol_uuids = []
    for protocol in link['protocols']:
        protocol_uuid = protocol['protocol_id']
        protocol_uuids.append(protocol_uuid)

    return {"process_uuid": process_uuid, "input_file_uuids": link["inputs"], "output_file_uuids": link["outputs"],
            "protocol_uuids": protocol_uuids}


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
