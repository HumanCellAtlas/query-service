import enum

from sqlalchemy import Column, String, Enum, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from dcpquery.db.models import SQLAlchemyBase
from dcpquery.db.models.base import DCPModelMixin
from dcpquery.db.models.modules import Ontology, Accession, Publication, CellMorphology, GrowthCondition, TimeCourse, \
    PlateBasedSequencing, CauseOfDeath, FamilialRelationship, MedicalHistory, StateOfSpecimen, PreservationStorage


class Biomaterial(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "biomaterials"
    ncbi_taxon_id = Column(String)
    discriminator = Column('type', String(50))
    accessions = relationship(Accession, secondary="biomaterial_accession_join_table")
    biomaterial_id = Column(String)
    name = Column(String)
    description = Column(String)
    genotype = Column(String)
    body = Column(MutableDict.as_mutable(JSONB))
    processes = relationship("Process", secondary="biomaterial_process_join_table")
    __mapper_args__ = {'polymorphic_on': discriminator}


class BiomaterialProcessJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "biomaterial_process_join_table"
    process = relationship("Process")
    biomaterial = relationship(Biomaterial)


class BiomaterialAccessionJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "biomaterial_accession_join_table"
    accession = relationship(Accession)
    biomaterial = relationship(Biomaterial)


class CellLineTypeEnum(enum.Enum):
    pass


class CellLine(Biomaterial, SQLAlchemyBase):
    __tablename__ = "cell_lines"
    id = Column(UUID, ForeignKey('biomaterials.uuid'), primary_key=True)
    type = Column(Enum(CellLineTypeEnum))
    cell_type = relationship(Ontology)
    model_organ = relationship(Ontology)
    publications = relationship(Publication, secondary="cell_line_publication_join_table")
    cell_cycle = relationship(Ontology)
    cell_morphology = relationship(CellMorphology)
    growth_condition = relationship(GrowthCondition)
    tissue = relationship(Ontology)
    disease = relationship(Ontology)  # should this be m2m?
    genus_species = relationship(Ontology)
    time_course = relationship(TimeCourse)
    __mapper_args__ = {'polymorphic_identity': 'cell_line'}


class CellLinePublicationJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "cell_line_publication_join_table"
    cell_line = relationship(CellLine)
    publication = relationship(Publication)


class CellTypeOntology(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "cell_type_ontologies"
    pass


class CellSuspension(Biomaterial, SQLAlchemyBase):
    __tablename__ = "cell_suspension"
    id = Column(UUID, ForeignKey('biomaterials.uuid'), primary_key=True)
    growth_conditions = relationship(GrowthCondition)
    cell_morphology = relationship(CellMorphology)
    genus_species = relationship(Ontology)  # this is an array in the dcp schema?
    selected_cell_types = relationship(Ontology, secondary="cell_suspension_cell_type_ontology_join_table")
    estimated_cell_count = Column(Integer)
    plate_based_sequencing = relationship(PlateBasedSequencing)
    time_course = relationship(TimeCourse)
    __mapper_args__ = {'polymorphic_identity': 'cell_suspension'}


class CellSuspensionCellTypeOntologyJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "cell_suspension_cell_type_ontology_join_table"
    cell_suspension = relationship(CellSuspension)
    cell_type_ontology = relationship(CellTypeOntology)


class IsLivingEnum(enum.Enum):
    pass


class SexEnum(enum.Enum):
    pass


class DiseaseOntology(Ontology, SQLAlchemyBase):
    pass


class DonorOrganism(Biomaterial, SQLAlchemyBase):
    __tablename__ = "donor_organism"
    id = Column(UUID, ForeignKey('biomaterials.uuid'), primary_key=True)
    is_living = Column(Enum(IsLivingEnum))
    development_stage = relationship(Ontology)
    sex = Column(Enum(SexEnum))
    # todo make many to many
    strain = relationship(Ontology)  # null if human
    bmi = Column(Integer)  # null if mouse
    ethnicity = relationship(Ontology)  # null if mouse
    genus_species = relationship(Ontology)
    organism_age = Integer
    organism_age_unit = relationship(Ontology)
    diseases = relationship(DiseaseOntology, secondary="donor_organism_disease_ontology_join_table")
    cause_of_death = relationship(CauseOfDeath)
    familial_relationship = relationship(FamilialRelationship)
    medical_history = relationship(MedicalHistory)
    time_course = relationship(TimeCourse)
    __mapper_args__ = {'polymorphic_identity': 'donor_organism'}


class DonorOrganismDiseaseOntologyJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "donor_organism_disease_ontology_join_table"
    donor_organism = relationship(DonorOrganism)
    disease_ontology = relationship(DiseaseOntology)


class SpecimenFromOrganism(Biomaterial, SQLAlchemyBase):
    __tablename__ = "specimen_from_organism"
    id = Column(UUID, ForeignKey('biomaterials.uuid'), primary_key=True)
    organ = relationship(Ontology)
    genus_species = relationship(Ontology)
    organ_parts = relationship(Ontology) # TODO Qx should this be m2m?
    diseases = relationship(DiseaseOntology, secondary="specimen_from_organism_disease_ontology_join_table")
    state_of_specimen = relationship(StateOfSpecimen)
    preservation_storage = relationship(PreservationStorage)
    collection_time = Column(DateTime)
    __mapper_args__ = {'polymorphic_identity': 'specimen_from_organism'}


class SpecimenFromOrganismDiseaseOntologyJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "specimen_from_organism_disease_ontology_join_table"
    donor_organism = relationship(DonorOrganism)
    disease_ontology = relationship(DiseaseOntology)


class Organoid(Biomaterial, SQLAlchemyBase):
    __tablename__ = "organoid"
    id = Column(UUID, ForeignKey('biomaterials.uuid'), primary_key=True)
    model_organ = relationship(Ontology)
    genus_species = relationship(Ontology)
    model_organ_part = relationship(Ontology)
    age = Column(Integer)
    age_unit = relationship(Ontology)
    __mapper_args__ = {'polymorphic_identity': 'organoid'}
