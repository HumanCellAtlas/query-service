from dcpquery import config
from dcpquery.db.models.biomaterial import (CellSuspension, DonorOrganism, Biomaterial, Specimen, CellLine,
                                            Organoid)
from dcpquery.db.models.join_tables import BiomaterialAccessionJoinTable, CellLinePublicationJoinTable, \
    CellSuspensionCellTypeOntologyJoinTable, DonorOrganismDiseaseOntologyJoinTable
from dcpquery.etl.load.utils import check_data
from dcpquery.etl.load.modules import (get_or_create_ontology, get_or_create_cause_of_death,
                                       get_or_create_family_relationship, get_or_create_medical_history,
                                       get_or_create_time_course,
                                       get_or_create_plate_based_sequencing, get_or_create_cell_morphology,
                                       get_or_create_growth_conditions,
                                       get_or_create_accession,
                                       get_or_create_preservation_storage, get_or_create_publication)


@check_data
def create_biomaterial(data):
    accessions_list = []
    for accession in data.get('accessions', []):
        accessions_list.append(get_or_create_accession(accession))

    biomaterial = Biomaterial(
        biomaterial_id=data.get('biomaterial_id'),
        ncbi_taxon_id=data.get('ncbi_taxon_id'),
        name=data.get('biomaterial_name'),
        description=data.get('biomaterial_description'),
        genotype=data.get('genotype'),
        body=data,
    )
    config.db_session.add(biomaterial)
    for accession in accessions_list:
        config.db_session.add(BiomaterialAccessionJoinTable(accession=accession, biomaterial=biomaterial))


def create_cell_suspension(data):
    accessions_list = []
    selected_cells_list = []
    for accession in data.get('accessions', []):
        accessions_list.append(get_or_create_accession(accession))
    growth_conditions = get_or_create_growth_conditions(data.get('growth_conditions'))
    cell_morphology = get_or_create_cell_morphology(data.get('cell_morphology'))
    genus_species = get_or_create_ontology(data.get("genus_species", [None])[0])
    time_course = get_or_create_time_course(data.get('time_course'))
    for cell in data.get('selected_cell_types', []):
        selected_cells_list.append(get_or_create_ontology(cell))
    plate_based_sequencing = get_or_create_plate_based_sequencing(data.get("plate_based_sequencing"))
    cell_suspension = CellSuspension(
        discriminator='cell_suspension',
        uuid=data.get('provenance', {}).get("document_id"),
        biomaterial_id=data.get('biomaterial_id'),
        ncbi_taxon_id=data.get('ncbi_taxon_id'),
        name=data.get('biomaterial_name'),
        description=data.get('biomaterial_description'),
        genotype=data.get('genotype'),
        body=data,
        growth_conditions=growth_conditions,
        cell_morphology=cell_morphology,
        genus_species=genus_species,
        estimated_cell_count=data.get("estimated_cell_count"),
        plate_based_sequencing=plate_based_sequencing,
        time_course=time_course
    )
    config.db_session.add(cell_suspension)
    for accession in accessions_list:
        config.db_session.add(BiomaterialAccessionJoinTable(accession=accession, biomaterial=cell_suspension))
    for cell in selected_cells_list:
        config.db_session.add(
            CellSuspensionCellTypeOntologyJoinTable(cell_type_ontology=cell, cell_suspension=cell_suspension))


def create_donor_organism(data):
    disease_list = []
    accessions_list = []
    for accession in data.get('accessions', []):
        accessions_list.append(get_or_create_accession(accession))
    try:
        organism_age = int(data.get("organism_age"))
    except:
        organism_age = None

    development_stage = get_or_create_ontology(data.get("development_stage"))
    genus_species = get_or_create_ontology(data.get("genus_species", [None])[0])
    organism_age_unit = get_or_create_ontology(data.get("organism_age_unit"))
    cause_of_death = get_or_create_cause_of_death(data.get('cause_of_death'))
    # todo find and check med history, family, timecourse
    medical_history = get_or_create_medical_history(data.get("medical_history"))
    familial_relationship = get_or_create_family_relationship(data)
    time_course = get_or_create_time_course(data)
    for disease in data.get('diseases', []):
        disease_list.append(get_or_create_ontology(disease))
    # todo handle mouse strain, bmi and ethnicity
    donor_organism = DonorOrganism(
        discriminator='donor_organism',
        biomaterial_id=data.get('biomaterial_id'),
        ncbi_taxon_id=data.get('ncbi_taxon_id'),
        name=data.get('biomaterial_name'),
        description=data.get('biomaterial_description'),
        genotype=data.get('genotype'),
        body=data,
        is_living=data.get("is_living"),
        development_stage=development_stage,
        sex=data.get('sex'),
        genus_species=genus_species,
        organism_age=organism_age,
        organism_age_unit=organism_age_unit,
        cause_of_death=cause_of_death,
        familial_relationship=familial_relationship,
        medical_history=medical_history,
        time_course=time_course
    )
    config.db_session.add(donor_organism)
    for disease in disease_list:
        config.db_session.add(
            DonorOrganismDiseaseOntologyJoinTable(donor_organism=donor_organism, disease_ontology=disease))
    for accession in accessions_list:
        config.db_session.add(BiomaterialAccessionJoinTable(accession=accession, biomaterial=donor_organism))


def create_specimen_from_organism(data):
    accessions_list = []
    disease_list = []
    organ = get_or_create_ontology(data.get('organ'))
    # todo make this m2m?
    organ_parts = get_or_create_ontology(data.get('organ_parts', [None])[0])
    # state_of_specimen = get_or_create_specimen_state(data.get('state_of_specimen'))
    preservation_storage = get_or_create_preservation_storage(data.get('preservation_storage'))
    genus_species = get_or_create_ontology(data.get("genus_species", [None])[0])
    for accession in data.get('accessions', []):
        accessions_list.append(get_or_create_accession(accession))
    for disease in data.get('diseases', []):
        disease_list.append(get_or_create_ontology(disease))
    specimen = Specimen(
        biomaterial_id=data.get('biomaterial_id'),
        discriminator='specimen_from_organism',
        ncbi_taxon_id=data.get('ncbi_taxon_id'),
        name=data.get('biomaterial_name'),
        description=data.get('biomaterial_description'),
        genotype=data.get('genotype'),
        body=data,
        organ=organ,
        genus_species=genus_species,
        organ_parts=organ_parts,
        # state_of_specimen=state_of_specimen,
        preservation_storage=preservation_storage,
        collection_time=data.get('collection_time')
    )
    config.db_session.add(specimen)
    for accession in accessions_list:
        config.db_session.add(BiomaterialAccessionJoinTable(accession=accession, biomaterial=biomaterial))


def create_cell_line(data):
    accessions_list = []
    publications_list = []
    cell_type = get_or_create_ontology(data.get('cell_type'))
    model_organ = get_or_create_ontology(data.get('model_organ'))
    cell_cycle = get_or_create_ontology(data.get('cell_cycle'))
    cell_morphology = get_or_create_cell_morphology(data.get('cell_morphology'))
    growth_condition = get_or_create_growth_conditions(data.get('growth_conditions'))
    tissue = get_or_create_ontology(data.get('tissue'))
    disease = get_or_create_ontology(data.get('disease'))
    genus_species = get_or_create_ontology(data.get('genus_species'))
    time_course = get_or_create_time_course(data.get('timecourse'))
    for accession in data.get('accessions', []):
        accessions_list.append(get_or_create_accession(accession))

    for publication in data.get('publications', []):
        publications_list.append(get_or_create_publication(publication))

    cell_line = CellLine(
        discriminator="cell_line",
        biomaterial_id=data.get('biomaterial_id'),
        ncbi_taxon_id=data.get('ncbi_taxon_id'),
        name=data.get('biomaterial_name'),
        description=data.get('biomaterial_description'),
        genotype=data.get('genotype'),
        body=data,
        type=data.get('type'),
        cell_type=cell_type,
        model_organ=model_organ,
        cell_cycle=cell_cycle,
        cell_morphology=cell_morphology,
        growth_condition=growth_condition,
        tissue=tissue,
        disease=disease,
        genus_species=genus_species,
        time_course=time_course
    )
    config.db_session.add(cell_line)
    for accession in accessions_list:
        config.db_session.add(BiomaterialAccessionJoinTable(accession=accession, biomaterial=cell_line))
    for publication in publications_list:
        config.db_session.add(CellLinePublicationJoinTable(cell_line=cell_line, publication=publication))
    return cell_line


def create_organoid(data):
    accessions_list = []
    model_organ = get_or_create_ontology(data.get('model_organ'))
    age = int(data.get('age')) if data.get('age') else None
    genus_species = get_or_create_ontology(data.get('genus_species'))
    model_organ_part = get_or_create_ontology(data.get('model_organ_part'))
    age_unit = get_or_create_ontology(data.get('age_unit'))
    for accession in data.get('accessions', []):
        accessions_list.append(get_or_create_accession(accession))

    biomaterial = Organoid(
        discriminator='organoid',
        biomaterial_id=data.get('biomaterial_id'),
        ncbi_taxon_id=data.get('ncbi_taxon_id'),
        name=data.get('biomaterial_name'),
        description=data.get('biomaterial_description'),
        genotype=data.get('genotype'),
        body=data,
        age=int(data.get('age')),
        model_organ=model_organ,
        genus_species=genus_species,
        model_organ_part=model_organ_part,
        age_unit=age_unit
    )
    config.db_session.add(biomaterial)
    for accession in accessions_list:
        config.db_session.add(BiomaterialAccessionJoinTable(accession=accession, biomaterial=biomaterial))
