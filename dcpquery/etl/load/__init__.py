from dcpquery.etl.load.biomaterials import (get_or_create_cell_suspension, get_or_create_donor_organism,
                                            get_or_create_specimen_from_organism, get_or_create_cell_line,
                                            get_or_create_organoid)
from dcpquery.etl.load.data_files import get_or_create_sequence_file, get_or_create_file
from dcpquery.etl.load.processes import get_or_create_process
from dcpquery.etl.load.projects import get_or_create_project
from dcpquery.etl.load.protocols import (get_or_create_dissociation_protocol,
                                         get_or_create_library_preparation_protocol,
                                         get_or_create_sequencing_protocol, get_or_create_enrichment_protocol,
                                         get_or_create_collection_protocol, get_or_create_differentiation_protocol,
                                         get_or_create_analysis_protocol, get_or_create_ipsc_induction_protocol)


def handle_all_schema_types(schema_type, schema_version, file_data, track_uuids, links_data):
    # file_data = data.get('body')
    if schema_type == 'cell_suspension':
        cell_suspension = get_or_create_cell_suspension(file_data)
        track_uuids[cell_suspension.uuid] = 'biomaterial'
    if schema_type == 'dissociation_protocol':
        diss_protocol = get_or_create_dissociation_protocol(file_data)
        track_uuids[diss_protocol.uuid] = 'protocol'
    if schema_type == 'donor_organism':
        donor_org = get_or_create_donor_organism(file_data)
        track_uuids[donor_org.uuid] = 'biomaterial'
    if schema_type == 'library_preparation_protocol':
        lib_prep_protocol = get_or_create_library_preparation_protocol(file_data)
        track_uuids[lib_prep_protocol.uuid] = 'protocol'
    if schema_type == 'links':
        links_data = file_data
    if schema_type == 'process':
        process = get_or_create_process(file_data, analysis=False)
        track_uuids[process.uuid] = 'process'
    if schema_type == 'project':
        project = get_or_create_project(file_data)
        track_uuids['project'] = project.uuid
    if schema_type == 'sequence_file':
        seq_file = get_or_create_sequence_file(file_data)
        track_uuids[seq_file.uuid] = 'file'
    if schema_type == 'sequencing_protocol':
        seq_protocol = get_or_create_sequencing_protocol(file_data)
        track_uuids[seq_protocol.uuid] = 'protocol'
    if schema_type == 'specimen_from_organism':
        spec_from_org = get_or_create_specimen_from_organism(file_data)
        track_uuids[spec_from_org.uuid] = 'biomaterial'
    if schema_type == 'enrichment_protocol':
        enrich_protocol = get_or_create_enrichment_protocol(file_data)
        track_uuids[enrich_protocol.uuid] = 'protocol'
    if schema_type == 'collection_protocol':
        collection_proto = get_or_create_collection_protocol(file_data)
        track_uuids[collection_proto.uuid] = 'protocol'
    if schema_type == 'cell_line':
        cell_line = get_or_create_cell_line(file_data)
        track_uuids[cell_line.uuid] = 'biomaterial'
    if schema_type == 'differentiation_protocol':
        diff_proto = get_or_create_differentiation_protocol(file_data)
        track_uuids[diff_proto.uuid] = 'protocol'
    if schema_type == 'analysis_file':
        analysis_file = get_or_create_file(file_data)
        track_uuids[analysis_file.uuid] = 'file'
    if schema_type == 'analysis_process':
        analysis_process = get_or_create_process(file_data, analysis=True)
        track_uuids[analysis_process.uuid] = 'process'

    if schema_type == 'analysis_protocol':
        analysis_protocol = get_or_create_analysis_protocol(file_data)
        track_uuids[analysis_protocol.uuid] = 'protocol'
    if schema_type == 'supplementary_file':
        supp_file = get_or_create_file(file_data)
        track_uuids[supp_file.uuid] = 'file'
    if schema_type == 'ipsc_induction_protocol':
        ipsc_protocol = get_or_create_ipsc_induction_protocol(file_data)
        track_uuids[ipsc_protocol.uuid] = 'protocol'
    if schema_type == 'organoid':
        organoid = get_or_create_organoid(file_data)
        track_uuids[organoid.uuid] = 'biomaterial'
    return track_uuids, links_data
