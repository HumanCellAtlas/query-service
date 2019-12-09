import uuid
from uuid import UUID

from dcpquery import config
from dcpquery.db.models.enums import StorageMethodEnum, PreservationMethodEnum, NutritionalStateEnum, WellQualityEnum, \
    BarcodeReadEnum, AccessionTypeEnum
from dcpquery.db.models.modules import Funder, Contributor, Accession, Ontology, Link, Publication, CauseOfDeath, \
    MedicalHistory, TimeCourse, GrowthCondition, CellMorphology, PlateBasedSequencing, PurchasedReagent, TenX, \
    PreservationStorage, Barcode, Task, Parameter
from dcpquery.etl.load.utils import check_data
from dcpquery.etl.load.admins import get_or_create_user


def get_or_create_accession(accession_id, type):
    accession = Accession.create(id=accession_id, type=AccessionTypeEnum(type))
    return accession


@check_data
def get_or_create_ontology(data):
    try:
        ontology = Ontology.get_or_create(text=data.get('text'), ontology=data.get('ontology'),
                                          ontology_label=data.get('ontology_label'))
    except Exception as e:
        import pdb
        pdb.set_trace()
        print(e)
    return ontology


@check_data
def create_funder(data):
    funder = Funder.create(
        grant_id=data.get('grant_id'), grant_title=data.get('grant_title'), organization=data.get('organization'))
    return funder


@check_data
def get_or_create_contributor(data):
    user = get_or_create_user(data)
    project_role = get_or_create_ontology(data.get("project_role"))
    contributor = Contributor.create(user=user, institution=data.get("institution"), lab=data.get("laboratory"),
                                     corresponding_contributor=data.get("corresponding_contributor"),
                                     project_role=project_role)
    return contributor


@check_data
def get_or_create_publication(data):
    authors = " ".join(data.get('authors'))
    publication_url = Link(url=data.get('url'))
    publication = Publication.create(authors=authors, title=data.get('title'), doi=data.get('doi'), url=publication_url)
    return publication


@check_data
def get_or_create_url_link(data):
    link = Link.create(url=data)
    return link


@check_data
def get_or_create_cause_of_death(data):
    cod = CauseOfDeath.create(
        cause_of_death=data.get('cause_of_death'),
        cold_perfused=data.get('cold_perfused'),
        days_on_ventilator=data.get('days_on_ventilator'),
        hardy_scale=data.get('hardy_scale'),
        time_of_death=data.get('time_of_death')
    )
    return cod


# Todo
@check_data
def get_or_create_family_relationship(data):
    return None


@check_data
def get_or_create_medical_history(data):
    nutritional_state = NutritionalStateEnum(data.get('nutritional_state')) if data.get('nutritional_state') else None
    medical_history = MedicalHistory.create(
        alcohol_history=data.get('alcohol_history'),
        medication=data.get('medication'),
        smoking_history=data.get('smoking_history'),
        nutritional_state=nutritional_state,
        test_results=data.get('test_results'),
        treatment=data.get('treatment'))
    return medical_history


@check_data
def get_or_create_time_course(data):
    time_course = TimeCourse.create(value=data.get('value'), unit=data.get('unit'), relevance=data.get('relevance'))
    return time_course


@check_data
def get_or_create_growth_conditions(data):
    if data is None:
        return None
    growth_condition = GrowthCondition.create(
        passage_number=data.get('passage_number'),
        growth_medium=data.get('growth_medium'),
        culture_environment=data.get('culture_environment'))
    return growth_condition


@check_data
def get_or_create_cell_morphology(data):
    cell_size_unit = get_or_create_ontology(data.get('cell_size_unit'))
    cell_morph = CellMorphology.create(
        cell_morphology=data.get('cell_morphology'),
        cell_size=data.get('cell_size'),
        cell_size_unit=cell_size_unit,
        percent_cell_viability=data.get('pecent_cell_viability'),
        cell_viability_method=data.get('cell_viability_method'),
        cell_viability_result=data.get('cell_viability_result'),
        percent_necrosis=data.get('percent_necrosis')
    )
    return cell_morph


@check_data
def get_or_create_plate_based_sequencing(data):
    plate = PlateBasedSequencing.create(plate_label=data.get('plate_label'),
                                        well_label=WellQualityEnum(data.get('well_label')),
                                        well_quality=data['well_quality'])
    return plate


@check_data
def get_or_create_reagent(data):
    purchased_reagent = PurchasedReagent.create(retail_name=data.get('retail_name'),
                                                catalog_number=data.get('catalog_number'),
                                                manufacturer=data.get('manufacturer'),
                                                lot_number=data.get('lot_number'),
                                                expiry_date=data.get('expiry_date'),
                                                kit_titer=data.get('kit_titer'))
    return purchased_reagent


@check_data
def get_or_create_ten_x(data):
    tenx = TenX.create(
        fastq_method=data.get('fastq'),
        fastq_method_version=data.get('fastq_method_version'),
        pooled_channels=data.get('pooled_channels'),
        drop_uniformity=data.get('drop_uniformity')
    )
    return tenx


@check_data
def get_or_create_preservation_storage(data):
    storage_time_unit = get_or_create_ontology(data.get('storage_time_unit'))
    storage_time = int(data.get('storage_time')) if data.get('storage_time') else None
    storage_method = StorageMethodEnum(data.get('storage_method')) if data.get('storage_method') else None
    preservation_method = PreservationMethodEnum(data.get('preservation_method')) if data.get(
        'preservation_method') else None
    preservation_storage = PreservationStorage.create(
        storage_method=storage_method,
        storage_time=storage_time,
        storage_time_unit=storage_time_unit,
        preservation_method=preservation_method
    )
    return preservation_storage


# @check_data
# def get_or_create_specimen_state(data):
#     # circular import
#     from dcpquery.etl.load import get_or_create_file
#
#     image_list = []
#     # todo  get actual image file names
#     for file in data.get('images', []):
#         image_list.append(get_or_create_file(file))
#     state_of_specimen = StateOfSpecimen(autolysis_score=data.get('autolysis_score'))
#     config.db_session.add(state_of_specimen)
#     for file in image_list:
#         config.db_session.add(SpecimenFileJoinTable(state_of_specimen=state_of_specimen, file=file))
#     return state_of_specimen


@check_data
def get_or_create_barcode(data):
    barcode = Barcode.create(
        barcode_offset=data.get('barcode_offset'),
        barcode_length=data.get('barcode_length'),
        barcode_read=BarcodeReadEnum(data.get('barcode_read')),
        white_list_file=data.get('white_list_file'))
    return barcode


# Todo implement
@check_data
def get_or_create_task(data):
    task = Task.create(name=data.get('task_name'),
                       docker_image=data.get('docker_image'),
                       disk_size=data.get('disk_size'),
                       start_time=data.get('start_time'),
                       stop_time=data.get('stop_time'),
                       memory=data.get('memory'),
                       zone=data.get('zone'),
                       log_err=data.get('log_err'),
                       log_out=data.get('log_out'),
                       cpus=data.get('cpus'),
                       )
    return task


@check_data
def get_or_create_parameter(data):
    parameter = Parameter.create(name=data.get('parameter_name'), value=data.get('parameter_value'))
    return parameter
