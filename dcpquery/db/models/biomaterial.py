from sqlalchemy import Column, String, Enum, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from dcpquery.db.models import SQLAlchemyBase
from dcpquery.db.models.base import DCPModelMixin
from dcpquery.db.models.enums import CellLineTypeEnum, IsLivingEnum, SexEnum
from dcpquery.db.models.modules import Ontology, Accession, Publication, CellMorphology, GrowthCondition, TimeCourse, \
    PlateBasedSequencing, CauseOfDeath, FamilialRelationship, MedicalHistory, PreservationStorage


class Biomaterial(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "biomaterials"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    discriminator = Column('type', String(50))
    ncbi_taxon_id = Column(String)
    biomaterial_id = Column(String)
    name = Column(String)
    description = Column(String)
    genotype = Column(String)
    body = Column(MutableDict.as_mutable(JSONB))
    accessions = relationship(Accession, secondary="biomaterial_accession_join_table")
    processes = relationship("Process", secondary="process_biomaterial_join_table")
    __mapper_args__ = {'polymorphic_on': discriminator}


class CellLine(Biomaterial, SQLAlchemyBase):
    __tablename__ = "cell_lines"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    discriminator = 'cell_line'
    uuid = Column(UUID, ForeignKey('biomaterials.uuid'), primary_key=True)
    type = Column(Enum(CellLineTypeEnum))
    publications = relationship(Publication, secondary="cell_line_publication_join_table")
    cell_morphology_uuid = Column(UUID, ForeignKey('cell_morphologies.uuid'))
    cell_morphology = relationship(CellMorphology)
    growth_condition = relationship(GrowthCondition)
    growth_condition_uuid = Column(UUID, ForeignKey('growth_conditions.uuid'))
    time_course = relationship(TimeCourse)
    time_course_uuid = Column(UUID, ForeignKey('time_courses.uuid'))
    cell_type_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    cell_type = relationship(Ontology, foreign_keys=[cell_type_uuid])
    model_organ_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    model_organ = relationship(Ontology, foreign_keys=[model_organ_uuid])
    cell_cycle_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    cell_cycle = relationship(Ontology, foreign_keys=[cell_cycle_uuid])
    tissue_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    tissue = relationship(Ontology, foreign_keys=[tissue_uuid])
    disease_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    disease = relationship(Ontology, foreign_keys=[disease_uuid])  # todo qx should this be m2m?
    genus_species_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    genus_species = relationship(Ontology, foreign_keys=[genus_species_uuid])
    __mapper_args__ = {'polymorphic_identity': 'cell_line'}


# class CellTypeOntology(DCPModelMixin, SQLAlchemyBase):
#     __tablename__ = "cell_type_ontologies"
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#     discriminator = 'cell_type_ontology'
#     uuid = Column(UUID, ForeignKey('ontologies.uuid'), primary_key=True)


class CellSuspension(Biomaterial, SQLAlchemyBase):
    __tablename__ = "cell_suspensions"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    discriminator = 'cell_suspension'
    uuid = Column(UUID, ForeignKey('biomaterials.uuid'), primary_key=True)
    estimated_cell_count = Column(Integer)

    growth_conditions = relationship(GrowthCondition)
    growth_condition_uuid = Column(UUID, ForeignKey('growth_conditions.uuid'))
    cell_morphology = relationship(CellMorphology)
    cell_morphology_uuid = Column(UUID, ForeignKey('cell_morphologies.uuid'))
    genus_species_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    genus_species = relationship(Ontology, foreign_keys=[genus_species_uuid])  # this is an array in the dcp schema?
    cell_types = relationship(Ontology, secondary="cell_suspension_cell_type_ontology_join_table")
    plate_based_sequencing = relationship(PlateBasedSequencing)
    plate_based_sequencing_uuid = Column(UUID, ForeignKey('plate_based_sequencing.uuid'))
    time_course = relationship(TimeCourse)
    time_course_uuid = Column(UUID, ForeignKey('time_courses.uuid'))

    __mapper_args__ = {'polymorphic_identity': 'cell_suspension'}


class DiseaseOntology(Ontology, SQLAlchemyBase):
    __tablename__ = "disease_ontologies"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    discriminator = 'disease_ontology'
    uuid = Column(UUID, ForeignKey('ontologies.uuid'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'disease_ontologies'}


class DonorOrganism(Biomaterial, SQLAlchemyBase):
    __tablename__ = "donor_organism"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    discriminator = 'donor_organism'

    uuid = Column(UUID, ForeignKey('biomaterials.uuid'), primary_key=True)
    is_living = Column(Enum(IsLivingEnum))
    sex = Column(Enum(SexEnum))
    bmi = Column(Integer)  # null if mouse
    organism_age = Column(Integer)
    cause_of_death = relationship(CauseOfDeath)
    cause_of_death_uuid = Column(UUID, ForeignKey('causes_of_death.uuid'))
    familial_relationship = relationship(FamilialRelationship)
    familial_relationship_uuid = Column(UUID, ForeignKey('familial_relationships.uuid'))
    medical_history = relationship(MedicalHistory)
    medical_history_uuid = Column(UUID, ForeignKey('medical_histories.uuid'))
    time_course = relationship(TimeCourse)
    time_course_uuid = Column(UUID, ForeignKey('time_courses.uuid'))
    development_stage_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    development_stage = relationship(Ontology, foreign_keys=[development_stage_uuid])
    # todo make many to many
    strain_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    strain = relationship(Ontology, foreign_keys=[strain_uuid])  # null if human
    ethnicity_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    ethnicity = relationship(Ontology, foreign_keys=[ethnicity_uuid])  # null if mouse
    genus_species_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    genus_species = relationship(Ontology, foreign_keys=[genus_species_uuid])
    organism_age_unit_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    organism_age_unit = relationship(Ontology, foreign_keys=[organism_age_unit_uuid])
    diseases = relationship(DiseaseOntology, secondary="donor_organism_disease_ontology_join_table")
    __mapper_args__ = {'polymorphic_identity': 'donor_organism'}


class Specimen(Biomaterial, SQLAlchemyBase):
    __tablename__ = "specimens"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    uuid = Column(UUID, ForeignKey('biomaterials.uuid'), primary_key=True)
    discriminator = 'specimen'
    collection_time = Column(DateTime)
    organ_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    organ = relationship(Ontology, foreign_keys=[organ_uuid])
    genus_sepcies_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    genus_species = relationship(Ontology, foreign_keys=[genus_sepcies_uuid])
    organ_parts_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    organ_parts = relationship(Ontology, foreign_keys=[organ_parts_uuid])  # TODO Qx should this be m2m?
    # todo reinstate
    # state_of_speciemen_uuid = Column(UUID, ForeignKey('state_of_speicemens.uuid'))
    # state_of_specimen = relationship(StateOfSpecimen)
    preservation_storage_uuid = Column(UUID, ForeignKey('preservation_storage.uuid'))
    preservation_storage = relationship(PreservationStorage)
    diseases = relationship(DiseaseOntology, secondary="specimen_disease_ontology_join_table")
    __mapper_args__ = {'polymorphic_identity': 'specimen'}


class Organoid(Biomaterial, SQLAlchemyBase):
    __tablename__ = "organoid"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    uuid = Column(UUID, ForeignKey('biomaterials.uuid'), primary_key=True)
    discriminator = 'organoid'

    age = Column(Integer)
    age_unit_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    age_unit = relationship(Ontology, foreign_keys=[age_unit_uuid])
    model_organ_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    model_organ = relationship(Ontology, foreign_keys=[model_organ_uuid])
    genus_species_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    genus_species = relationship(Ontology, foreign_keys=[genus_species_uuid])
    model_organ_part_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    model_organ_part = relationship(Ontology, foreign_keys=[model_organ_part_uuid])
    __mapper_args__ = {'polymorphic_identity': 'organoid'}
