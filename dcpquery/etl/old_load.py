import logging
import re

from dcpquery import config
from dcpquery.db.models import Bundle, DCPMetadataSchemaType, File, BundleFileLink, Process, ProcessFileLink
from dcpquery.db.models.enums import ProcessConnectionTypeEnum
from dcpquery.db.models.process import ProcessBiomaterialJoinTable, ProcessFileJoinTable, ProcessProtocolJoinTable
from dcpquery.etl.load import handle_all_schema_types

logger = logging.getLogger(__name__)


class BundleLoader:
    def __init__(self):
        pass
        # schema_types = config.db_session.query(DCPMetadataSchemaType).with_entities(DCPMetadataSchemaType.name).all()
        # self.schema_types = [schema[0] for schema in schema_types]

    # def create_project(self, files):
    #     for file in files:
    #         if file['body']:
    #             if file['body'].get('describedBy', '').split('/')[-1] == 'project':
    #                 return Project(uuid=file['uuid'], version=file['version'])

    def load_bundle(self, bundle, extractor=None, transformer=None):
        bf_links = []
        # bundle_row = Bundle(uuid=bundle["uuid"],
        #                     version=bundle["version"],
        #                     manifest=bundle["manifest"],
        #                     aggregate_metadata=bundle["aggregate_metadata"])
        track_uuids = {}
        links_data = {}
        for file_data in bundle["files"]:
            filename = file_data.pop("name")
            # file_extension = get_file_extension(filename)
            schema_type = None
            # major_version = None
            # minor_version = None
            if file_data['body']:
                schema_type = file_data['body'].get('describedBy', '').split('/')[-1]
                schema_version = file_data['body'].get('describedBy', '').split('/')[-2]
                # major_version = schema_version.split('.')[0]
                # minor_version = schema_version.split('.')[1]

                track_uuids, links_data = handle_all_schema_types(schema_type, schema_version, file_data, track_uuids,
                                                                  links_data)
        links = links_data['links']
        project_uuid = track_uuids['project']
        for link in links:
            process_uuid = link['process']
            inputs = link['inputs']
            outputs = link['outputs']
            protocols = link['protocols']

            for input in inputs:
                if link['input_type'] == 'biomaterial':
                    ProcessBiomaterialJoinTable(
                        connection_type=ProcessConnectionTypeEnum('INPUT'),
                        process_uuid=process_uuid,
                        biomaterial_uuid=input,
                        project_uuid=project_uuid
                    )
                if link['input_type'] == 'file':
                    ProcessFileJoinTable(
                        connection_type=ProcessConnectionTypeEnum('INPUT'),
                        process_uuid=process_uuid,
                        file_uuid=input,
                        project_uuid=project_uuid
                    )
            for output in outputs:
                if link['output_type'] == 'biomaterial':
                    ProcessBiomaterialJoinTable.create(
                        connection_type=ProcessConnectionTypeEnum('OUTPUT'),
                        process_uuid=process_uuid,
                        biomaterial_uuid=output,
                        project_uuid=project_uuid
                    )
                if link['output_type'] == 'file':
                    ProcessFileJoinTable.create(
                        connection_type=ProcessConnectionTypeEnum('OUTPUT'),
                        process_uuid=process_uuid,
                        file_uuid=output,
                        project_uuid=project_uuid
                    )
            for protocol in protocols:
                ProcessProtocolJoinTable.create(
                    connection_type=ProcessConnectionTypeEnum('PROTOCOL'),
                    process_uuid=process_uuid,
                    protocol_uuid=protocol['protocol_id'],
                    project_uuid=project_uuid
                )



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
