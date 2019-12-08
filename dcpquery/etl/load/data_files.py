from dcpquery import config
from dcpquery.db.models.data_file import SequenceFile, DCPFile
from dcpquery.db.models.join_tables import SequenceFileAccessionJoinTable
from dcpquery.etl.load.utils import check_data
from dcpquery.etl.load.modules import get_or_create_accession


# use base function for analysis/suppplemental files
@check_data
def get_or_create_file(data):
    file = DCPFile(
        name=data.get('name'),
        format=data.get('format'),
        checksum=data.get('checksum'),
        file_description=data.get('file_description'),
        body=data,
    )
    config.db_session.add(file)
    return file


def handle_sequence_files(sequence_file_data):
    for file in sequence_file_data:
        get_or_create_sequence_file(file)


@check_data
def get_or_create_sequence_file(data):
    accession_objects = []
    body = data
    uuid = data.get('provenance', {}).get('document_id')
    name = data.get('file_core', {}).get('file_name')
    format = data.get('file_core', {}).get('format')
    accessions_list = data.get("insdc_run_accessions", [])
    # TODO figure out how to carry through checksum from bundle manifest
    checksum = "None"
    # todo content description, file description, lane index, read length, ?
    file = SequenceFile(
        uuid=uuid,
        discriminator="sequence_file",
        name=name,
        format=format,
        checksum=checksum,
        body=body,
        read_index=data.get("read_index"),
        libary_prep_id=data.get('libarry_prep_id')
    )
    config.db_session.add(file)
    for accession in accessions_list:
        accession_objects.append(get_or_create_accession(accession, "insdc_run"))
    config.db_session.add_all(accession_objects)
    for accession in accession_objects:
        create_file_accession_link(file, accession)


def create_file_accession_link(file, accession):
    config.db_session.add(SequenceFileAccessionJoinTable(sequence_file=file, accession=accession))
