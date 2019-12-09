from sqlalchemy.dialects.postgresql import UUID

from dcpquery import config
from dcpquery.db.models.enums import AnalysisRunTypeEnum
from dcpquery.db.models.process import Process, ProcessTaskJoinTable, ProcessParameterJoinTable
from dcpquery.etl.load.utils import check_data
from dcpquery.etl.load.modules import get_or_create_ontology, get_or_create_accession, get_or_create_task, \
    get_or_create_parameter


@check_data
def get_or_create_process(data, analysis):
    task_list = []
    parameter_list = []
    for task in data.get('tasks', []):
        task_list.append(get_or_create_task(task))
    for parameter in data.get('parameter', []):
        import pdb
        pdb.set_trace()
        parameter_list.append(get_or_create_parameter(parameter))
    uuid = data.get('provenance', {}).get("document_id")
    if not uuid:
        import pdb
        pdb.set_trace()

    print(f"MADISONNNNN THIS PROCESS HAS AN UUID: {uuid}")

    analysis_type = data.get('type', {}).get('text')
    accession = get_or_create_accession(data.get('accession'), "PROCESS")
    analysis_run_type = AnalysisRunTypeEnum(data.get('analysis_run_type')) if data.get('analysis_run_type') else None
    process = Process.get_or_create(
        uuid=uuid,
        analysis=analysis,
        body=data,
        name=data.get('name'),
        description=data.get('description'),
        location=data.get('location'),
        start_time=data.get('starttime'),
        end_time=data.get('endtime'),
        analysis_type=analysis_type,
        deviation_from_protocol=data.get('deviation_from_protocol'),
        accession=accession,
        input_bundle=data.get('input_bundle'),
        analysis_run_type=analysis_run_type
    )
    for task in task_list:
        ProcessTaskJoinTable.create(task=task, process=process)

    for parameter in parameter_list:
        ProcessParameterJoinTable.create(parameter=parameter, process=process)

    return process
