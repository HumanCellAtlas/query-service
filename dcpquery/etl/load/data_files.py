from dcpquery import config
from dcpquery.db.models.data_file import SequenceFile, SequenceFileAccessionJoinTable, DCPFile
from dcpquery.etl.load.modules import get_or_create_accession


# use base function for analysis/suppplemental files
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


def get_or_create_sequence_file(data):
    accession_objects = []
    body = data
    uuid = data['provenance']['document_id']
    name = data['file_core']['file_name']
    format = data['file_core']['format']
    accessions_list = data["insdc_run_accessions"]
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
        read_index=data["read_index"],
        libary_prep_id=data['libarry_prep_id']
    )
    config.db_session.add(file)
    for accession in accessions_list:
        accession_objects.append(get_or_create_accession(accession, "insdc_run"))
    config.db_session.add_all(accession_objects)
    for accession in accession_objects:
        create_file_accession_link(file, accession)


def create_file_accession_link(file, accession):
    config.db_session.add(SequenceFileAccessionJoinTable(sequence_file=file, accession=accession))
