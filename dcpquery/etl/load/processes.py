from dcpquery import config
from dcpquery.db.models.process import Process, ProcessTaskJoinTable, ProcessParameterJoinTable
from dcpquery.etl.load.utils import check_data
from dcpquery.etl.load.modules import get_or_create_ontology, get_or_create_accession, get_or_create_task, \
    get_or_create_parameter


@check_data
def create_process(data, analysis):
    task_list = []
    parameter_list = []
    for task in data.get('tasks', []):
        task_list.append(get_or_create_task(task))
    for parameter in data.get('parameter', []):
        parameter_list.append(get_or_create_parameter(parameter))
    type = get_or_create_ontology(data.get('type'))
    accession = get_or_create_accession(data.get('accession'), "PROCESS")
    process = Process(
        analysis=analysis,
        body=data,
        name=data.get('name'),
        description=data.get('description'),
        location=data.get('location'),
        start_time=data.get('starttime'),
        end_time=data.get('endtime'),
        type=type,
        deviation_from_protocol=data.get('deviation_from_protocol'),
        accession=accession,
        input_bundle=data.get('input_bundle'),
        analysis_run_type=data.get('analysis_run_type')
    )
    for task in task_list:
        config.db_session.add(ProcessTaskJoinTable(task=task, process=process))

    for parameter in parameter_list:
        config.db_session.add(ProcessParameterJoinTable(parameter=parameter, process=process))

