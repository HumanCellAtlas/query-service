from dcpquery.etl.load.biomaterials import (get_or_create_cell_suspension, get_or_create_donor_organism,
                                            get_or_create_specimen_from_organism, get_or_create_cell_line, get_or_create_organoid)
from dcpquery.etl.load.data_files import get_or_create_sequence_file, get_or_create_file
from dcpquery.etl.load.processes import get_or_create_process
from dcpquery.etl.load.projects import get_or_create_project
from dcpquery.etl.load.protocols import (get_or_create_dissociation_protocol, get_or_create_library_preparation_protocol,
                                         get_or_create_sequencing_protocol, get_or_create_enrichment_protocol,
                                         get_or_create_collection_protocol, get_or_create_differentiation_protocol,
                                         get_or_create_analysis_protocol, get_or_create_ipsc_induction_protocol)


def handle_all_schema_types(schema_type, schema_version, data):
    file_data = data.get('body')
    if schema_type == 'cell_suspension':
        get_or_create_cell_suspension(file_data)
    if schema_type == 'dissociation_protocol':
        get_or_create_dissociation_protocol(file_data)
    if schema_type == 'donor_organism':
        get_or_create_donor_organism(file_data)
    if schema_type == 'library_preparation_protocol':
        get_or_create_library_preparation_protocol(file_data)
    if schema_type == 'links':
        pass
    if schema_type == 'process':
        get_or_create_process(file_data, analysis=False)
    if schema_type == 'project':
        get_or_create_project(file_data)
    if schema_type == 'sequence_file':
        get_or_create_sequence_file(file_data)
    if schema_type == 'sequencing_protocol':
        get_or_create_sequencing_protocol(file_data)
    if schema_type == 'specimen_from_organism':
        get_or_create_specimen_from_organism(file_data)
    if schema_type == 'enrichment_protocol':
        get_or_create_enrichment_protocol(file_data)
    if schema_type == 'collection_protocol':
        get_or_create_collection_protocol(file_data)
    if schema_type == 'cell_line':
        get_or_create_cell_line(file_data)
    if schema_type == 'differentiation_protocol':
        get_or_create_differentiation_protocol(file_data)
    if schema_type == 'analysis_file':
        get_or_create_file(file_data)
    if schema_type == 'analysis_process':
        get_or_create_process(file_data, analysis=True)
    if schema_type == 'analysis_protocol':
        get_or_create_analysis_protocol(file_data)
    if schema_type == 'supplementary_file':
        get_or_create_file(file_data)
    if schema_type == 'ipsc_induction_protocol':
        get_or_create_ipsc_induction_protocol(file_data)
    if schema_type == 'organoid':
        get_or_create_organoid(file_data)
