from dcpquery import config
from dcpquery.db.models.modules import Funder, Contributor, Accession, Ontology, Link, Publication, CauseOfDeath, \
    MedicalHistory, TimeCourse, GrowthCondition, CellMorphology, PlateBasedSequencing, PurchasedReagent, TenX, \
    PreservationStorage, StateOfSpecimen, SpecimenFileJoinTable, Barcode


def get_or_create_accession(accession_id, type):
    accession = Accession(id=accession_id, type=type)
    config.db_session.add(accession)
    return accession


def get_or_create_ontology(data):
    ontology = Ontology(text=data.get('text'), ontology=data.get('ontology'), ontology_label=data.get('ontology_label'))
    config.db_session.add(ontology)
    return ontology


def create_funder(data):
    funder = Funder(
        grant_id=data.get('grant_id'), grant_title=data.get('grant_title'), organization=data.get('organization'))
    config.db_session.add(funder)
    return funder


def get_or_create_contributor(data):
    # TODO @madison
    user = get_or_create_user(data)
    project_role = get_or_create_ontology(data.get("project_role"))
    contributor = Contributor(user=user, institution=data.get("institution"), lab=data.get("laboratory"),
                              corresponding_contributor=data.get("corresponding_contributor"),
                              project_role=project_role)
    config.db_session.add(contributor)


def get_or_create_publication(data):
    authors = " ".join(data.get('authors'))
    publication_url = Link(url=data.get('url'))
    publication = Publication(authors=authors, title=data.get('title'), doi=data.get('doi'), url=publication_url)
    config.db_session.add(publication)
    return publication


def get_or_create_url_link(data):
    link = Link(url=data)
    config.db_session.add(link)
    return link


def get_or_create_cause_of_death(data):
    cod = CauseOfDeath(
        cause_of_death=data.get('cause_of_death'),
        cold_perfused=data.get('cold_perfused'),
        days_on_ventilator=data.get('days_on_ventilator'),
        hardy_scale=data.get('hardy_scale'),
        time_of_death=data.get('time_of_death')
    )
    config.db_session.add(cod)
    return cod


# Todo
def get_or_create_family_relationship(data):
    return


def get_or_create_medical_history(data):
    medical_history = MedicalHistory(alcohol_history=data.get('alcohol_history'),
                                     medication=data.get('medication'),
                                     smoking_history=data.get('smoking_history'),
                                     nutritional_state=data.get('nutritional_state'),
                                     test_results=data.get('test_results'),
                                     treatment=data.get('treatment'))
    config.db_session.add(medical_history)
    return medical_history


def get_or_create_time_course(data):
    time_course = TimeCourse(value=data.get('value'), unit=data.get('unit'), relevance=data.get('relevance'))
    config.db_session.add(time_course)
    return time_course


def get_or_create_growth_conditions(data):
    growth_condition = GrowthCondition(
        passage_number=data.get('passage_number'),
        growth_medium=data.get('growth_medium'),
        culture_environment=data.get('culture_environment'))
    config.db_session.add(growth_condition)
    return growth_condition


def get_or_create_cell_morphology(data):
    cell_size_unit = get_or_create_ontology(data.get('cell_size_unit'))
    cell_morph = CellMorphology(
        cell_morphology=data.get('cell_morphology'),
        cell_size=data.get('cell_size'),
        cell_size_unit=cell_size_unit,
        percent_cell_viability=data.get('pecent_cell_viability'),
        cell_viability_method=data.get('cell_viability_method'),
        cell_viability_result=data.get('cell_viability_result'),
        percent_necrosis=data.get('percent_necrosis')
    )
    config.db_session.add(cell_morph)
    return cell_morph


def get_or_create_plate_based_sequencing(data):
    plate = PlateBasedSequencing(plate_label=data['plate_label'], well_label=data['well_label'],
                                 well_quality=data['well_quality'])
    config.db_session.add(plate)
    return plate


def get_or_create_reagent(data):
    purchased_reagent = PurchasedReagent(retail_name=data.get('retail_name'),
                                         catalog_number=data.get('catalog_number'),
                                         manufacturer=data.get('manufacturer'),
                                         lot_number=data.get('lot_number'),
                                         expiry_date=data.get('expiry_date'),
                                         kit_titer=data.get('kit_titer'))
    config.db_session.add(purchased_reagent)
    return purchased_reagent


def get_or_create_ten_x(data):
    tenx = TenX(
        fastq_method=data.get('fastq'),
        fastq_method_version=data.get('fastq_method_version'),
        pooled_channels=data.get('pooled_channels'),
        drop_uniformity=data.get('drop_uniformity')
    )
    config.db_session.add(tenx)
    return tenx


def get_or_create_preservation_storage(data):
    storage_time_unit = get_or_create_ontology(data.get('storage_time_unit'))
    preservation_storage = PreservationStorage(
        storage_method=data.get('storage_method'),
        storage_time=int(data.get('storage_time')),
        storage_time_unit=storage_time_unit,
        preservation_method=data.get('preservation_method')
    )
    config.db_session.add(preservation_storage)
    return preservation_storage


def get_or_create_specimen_state(data):
    image_list = []
    # todo  get actual image file names
    for file in data.get('images'):
        image_list.append(get_or_create_file(file))
    state_of_specimen = StateOfSpecimen(autolysis_score=data.get('autolysis_score'))
    config.db_session.add(state_of_specimen)
    for file in image_list:
        config.db_session.add(SpecimenFileJoinTable(state_of_specimen=state_of_specimen, file=file))
    return state_of_specimen


def get_or_create_barcode(data):
    barcode = Barcode(barcode_offset=data.get('barcode_offset'), barcode_length=data.get('barcode_length'),
                   barcode_read=data.get('barcode_read'), white_list_file=data.get('white_list_file'))
    config.db_session.add(barcode)
    return barcode