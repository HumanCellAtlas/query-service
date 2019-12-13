import logging
import re

from dcpquery.db.models.enums import ProcessConnectionTypeEnum
from dcpquery.db.models.process import ProcessBiomaterialJoinTable, ProcessFileJoinTable, ProcessProtocolJoinTable
from dcpquery.etl.load import handle_all_schema_types

logger = logging.getLogger(__name__)


def load_bundle(bundle):
    aggregate_metadata = bundle['aggregate_metadata']
    track_uuids = {}
    links_data = []

    for key in aggregate_metadata:
        schema_type = key
        files = aggregate_metadata[key]
        if type(files) == dict:
            files = [files]
        for file in files:
            try:
                assert schema_type == file.get('describedBy', '').split('/')[-1]
                schema_version = file.get('describedBy', '').split('/')[-2]
            except Exception as e:
                logger.info(e)
            track_uuids, links_data = handle_all_schema_types(schema_type, schema_version, file, track_uuids,
                                                              links_data)

    try:
        project_uuid = track_uuids['project']
    except Exception as e:
        logger.info(f"no project for this bundle, {bundle['uuid']}, exception: {e}")
    for links in links_data:
        for link in links:
            process_uuid = link['process']
            inputs = link['inputs']
            outputs = link['outputs']
            protocols = link['protocols']

            for input in inputs:
                if link['input_type'] == 'biomaterial':
                    ProcessBiomaterialJoinTable.create(
                        connection_type=ProcessConnectionTypeEnum('INPUT'),
                        process_uuid=process_uuid,
                        biomaterial_uuid=input,
                        project_uuid=project_uuid
                    )
                if link['input_type'] == 'file':
                    ProcessFileJoinTable.create(
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
