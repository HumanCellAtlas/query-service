from dcpquery.etl.load.biomaterials import (create_cell_suspension, create_donor_organism,
                                            create_specimen_from_organism, create_cell_line, create_organoid)
from dcpquery.etl.load.data_files import get_or_create_sequence_file, get_or_create_file
from dcpquery.etl.load.processes import create_process
from dcpquery.etl.load.projects import create_project
from dcpquery.etl.load.protocols import (create_dissociation_protocol, create_library_preparation_protocol,
                                         create_sequencing_protocol, create_enrichment_protocol,
                                         create_collection_protocol, create_differentiation_protocol,
                                         create_analysis_protocol, create_ipsc_induction_protocol)


def handle_all_schema_types(schema_type, schema_version, data):
    file_data = data.get('body')
    if schema_type == 'cell_suspension':
        create_cell_suspension(file_data)
    if schema_type == 'dissociation_protocol':
        create_dissociation_protocol(file_data)
    if schema_type == 'donor_organism':
        create_donor_organism(file_data)
    if schema_type == 'library_preparation_protocol':
        create_library_preparation_protocol(file_data)
    if schema_type == 'links':
        pass
    if schema_type == 'process':
        create_process(file_data, analysis=False)
    if schema_type == 'project':
        create_project(file_data)
    if schema_type == 'sequence_file':
        get_or_create_sequence_file(file_data)
    if schema_type == 'sequencing_protocol':
        create_sequencing_protocol(file_data)
    if schema_type == 'specimen_from_organism':
        create_specimen_from_organism(file_data)
    if schema_type == 'enrichment_protocol':
        create_enrichment_protocol(file_data)
    if schema_type == 'collection_protocol':
        create_collection_protocol(file_data)
    if schema_type == 'cell_line':
        create_cell_line(file_data)
    if schema_type == 'differentiation_protocol':
        create_differentiation_protocol(file_data)
    if schema_type == 'analysis_file':
        get_or_create_file(file_data)
    if schema_type == 'analysis_process':
        create_process(file_data, analysis=True)
    if schema_type == 'analysis_protocol':
        create_analysis_protocol(file_data)
    if schema_type == 'supplementary_file':
        get_or_create_file(file_data)
    if schema_type == 'ipsc_induction_protocol':
        create_ipsc_induction_protocol(file_data)
    if schema_type == 'organoid':
        create_organoid(file_data)
