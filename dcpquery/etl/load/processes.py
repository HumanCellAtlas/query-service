from dcpquery.db.models.process import Process
from dcpquery.etl.load.modules import get_or_create_ontology, get_or_create_accession


def create_process(data):

    type = get_or_create_ontology(data.get('type'))
    accession = get_or_create_accession(data.get('accession'))
    process = Process(
        body=data,
        name=data.get('name'),
        description=data.get('description'),
        location=data.get('location'),
        start_time=data.get('starttime'),
        end_time=data.get('endtime'),
        type=type,
        deviation_from_protocol=data.get('deviation_from_protocol'),

    )

def create_analysis_process():
    pass