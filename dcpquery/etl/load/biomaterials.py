from sqlalchemy import DateTime

from dcpquery import config
from dcpquery.db.models.biomaterial import (CellSuspension, DonorOrganism, Biomaterial, Specimen, CellLine,
                                            Organoid)
from dcpquery.db.models.enums import CellLineTypeEnum, IsLivingEnum, SexEnum
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


def get_accessions(data):
    accessions_list = []
    for accession in data.get('biosamples_acessions', []):
        accessions_list.append(get_or_create_accession(accession))
    for accession in data.get('insdc_sample_accession', []):
        accessions_list.append(get_or_create_accession(accession))
    for accession in data.get('HDBR_accession', []):
        accessions_list.append(get_or_create_accession(accession))
    return accessions_list


@check_data
def get_or_create_biomaterial(data):
    accessions_list = get_accessions(data)

    biomaterial = Biomaterial.get_or_create(
        uuid=data.get('provenance', {}).get("document_id"),
        biomaterial_id=data.get('biomaterial_id'),
        ncbi_taxon_id=data.get('ncbi_taxon_id', [None])[0],
        name=data.get('biomaterial_name'),
        description=data.get('biomaterial_description'),
        genotype=data.get('genotype'),
        body=data,
    )
    for accession in accessions_list:
        BiomaterialAccessionJoinTable.create(accession=accession, biomaterial=biomaterial)
    return biomaterial


def get_or_create_cell_suspension(data):
    uuid = data.get('provenance', {}).get("document_id")

    accessions_list = get_accessions(data)
    selected_cells_list = []

    growth_conditions = get_or_create_growth_conditions(data.get('growth_conditions'))
    cell_morphology = get_or_create_cell_morphology(data.get('cell_morphology'))
    genus_species = get_or_create_ontology(data.get("genus_species", [None])[0])
    time_course = get_or_create_time_course(data.get('time_course'))
    for cell in data.get('selected_cell_types', []):
        selected_cells_list.append(get_or_create_ontology(cell))
    plate_based_sequencing = get_or_create_plate_based_sequencing(data.get("plate_based_sequencing"))
    cell_suspension = CellSuspension.get_or_create(
        uuid=uuid,
        biomaterial_id=data.get('biomaterial_id'),
        ncbi_taxon_id=data.get('ncbi_taxon_id', [None])[0],
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
    for accession in accessions_list:
        BiomaterialAccessionJoinTable.create(accession=accession, biomaterial=cell_suspension)
    for cell in selected_cells_list:
        CellSuspensionCellTypeOntologyJoinTable.create(cell_type_ontology=cell, cell_suspension=cell_suspension)
    return cell_suspension


def get_or_create_donor_organism(data):
    disease_list = []
    accessions_list = get_accessions(data)
    uuid = data.get('provenance', {}).get("document_id")

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
    familial_relationship = get_or_create_family_relationship(data.get('familial_relationships'))
    time_course = get_or_create_time_course(data.get('timecourse'))
    for disease in data.get('diseases', []):
        disease_list.append(get_or_create_ontology(disease))
    # todo handle mouse strain, bmi and ethnicity
    donor_organism = DonorOrganism.get_or_create(
        uuid=uuid,
        biomaterial_id=data.get('biomaterial_id'),
        ncbi_taxon_id=data.get('ncbi_taxon_id', [None])[0],
        name=data.get('biomaterial_name'),
        description=data.get('biomaterial_description'),
        genotype=data.get('genotype'),
        body=data,
        is_living=IsLivingEnum(data.get("is_living")),
        development_stage=development_stage,
        sex=SexEnum(data.get('sex')),
        genus_species=genus_species,
        organism_age=organism_age,
        organism_age_unit=organism_age_unit,
        cause_of_death=cause_of_death,
        familial_relationship=familial_relationship,
        medical_history=medical_history,
        time_course=time_course
    )
    for disease in disease_list:
        DonorOrganismDiseaseOntologyJoinTable.create(donor_organism=donor_organism, disease_ontology=disease)
    for accession in accessions_list:
        BiomaterialAccessionJoinTable.create(accession=accession, biomaterial=donor_organism)
    return donor_organism


def get_or_create_specimen_from_organism(data):
    uuid = data.get('provenance', {}).get("document_id")
    accessions_list = get_accessions(data)
    disease_list = []
    organ = get_or_create_ontology(data.get('organ'))
    # todo make this m2m?
    collection_time = data.get('collection_time')
    if collection_time and len(collection_time) < 10:
        collection_time = None
        print(f"FIX ME: collection_time on specimen_from_organsim {uuid}")
    organ_parts = get_or_create_ontology(data.get('organ_parts', [None])[0])
    # state_of_specimen = get_or_create_specimen_state(data.get('state_of_specimen'))
    preservation_storage = get_or_create_preservation_storage(data.get('preservation_storage'))
    genus_species = get_or_create_ontology(data.get("genus_species", [None])[0])
    for disease in data.get('diseases', []):
        disease_list.append(get_or_create_ontology(disease))
    specimen = Specimen.get_or_create(
        biomaterial_id=data.get('biomaterial_id'),
        uuid=uuid,
        ncbi_taxon_id=data.get('ncbi_taxon_id', [None])[0],
        name=data.get('biomaterial_name'),
        description=data.get('biomaterial_description'),
        genotype=data.get('genotype'),
        body=data,
        organ=organ,
        genus_species=genus_species,
        organ_parts=organ_parts,
        # state_of_specimen=state_of_specimen,
        preservation_storage=preservation_storage,
        collection_time=collection_time
    )
    for accession in accessions_list:
        BiomaterialAccessionJoinTable.create(accession=accession, biomaterial=specimen)
    return specimen


def get_or_create_cell_line(data):
    uuid = data.get('provenance', {}).get("document_id")

    accessions_list = get_accessions(data)
    publications_list = []
    cell_type = get_or_create_ontology(data.get('cell_type'))
    model_organ = get_or_create_ontology(data.get('model_organ'))
    cell_cycle = get_or_create_ontology(data.get('cell_cycle'))
    cell_morphology = get_or_create_cell_morphology(data.get('cell_morphology'))
    growth_condition = get_or_create_growth_conditions(data.get('growth_conditions'))
    tissue = get_or_create_ontology(data.get('tissue'))
    disease = get_or_create_ontology(data.get('disease'))
    genus_species = get_or_create_ontology(data.get('genus_species', [None])[0])
    time_course = get_or_create_time_course(data.get('timecourse'))

    for publication in data.get('publications', []):
        publications_list.append(get_or_create_publication(publication))

    cell_line = CellLine.get_or_create(
        discriminator="cell_line",
        uuid=uuid,
        biomaterial_id=data.get('biomaterial_id'),
        ncbi_taxon_id=data.get('ncbi_taxon_id', [None])[0],
        name=data.get('biomaterial_name'),
        description=data.get('biomaterial_description'),
        genotype=data.get('genotype'),
        body=data,
        type=CellLineTypeEnum(data.get('type')),
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
    for accession in accessions_list:
        BiomaterialAccessionJoinTable.create(accession=accession, biomaterial=cell_line)
    for publication in publications_list:
        CellLinePublicationJoinTable.create(cell_line=cell_line, publication=publication)
    return cell_line


def get_or_create_organoid(data):
    uuid = data.get('provenance', {}).get("document_id")

    accessions_list = get_accessions(data)
    model_organ = get_or_create_ontology(data.get('model_organ'))
    age = int(data.get('age')) if data.get('age') else None
    genus_species = get_or_create_ontology(data.get('genus_species', [None])[0])
    model_organ_part = get_or_create_ontology(data.get('model_organ_part'))
    age_unit = get_or_create_ontology(data.get('age_unit'))

    organioid = Organoid.get_or_create(
        uuid=uuid,
        biomaterial_id=data.get('biomaterial_id'),
        ncbi_taxon_id=data.get('ncbi_taxon_id', [None])[0],
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
    for accession in accessions_list:
        BiomaterialAccessionJoinTable.create(accession=accession, biomaterial=organioid)
    return organioid
