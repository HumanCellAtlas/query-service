import enum

from sqlalchemy import Column, String, Boolean, Integer, Enum, DateTime
from sqlalchemy.orm import relationship

from dcpquery.db.models import SQLAlchemyBase
from dcpquery.db.models.admin import User
from dcpquery.db.models.base import DCPModelMixin


class Contributor(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "contributors"
    user = relationship(User)
    institution = Column(String)  # make table or enum?
    lab = Column(String)  # make table?
    corresponding_contributor = Column(Boolean)
    project_role = relationship("Ontology")
    projects = relationship("Project", secondary="project_contributor_join_table")


class Publication(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "publications"
    authors = Column(String)
    # authors = relationship("User", secondary="publication_author_join_table")
    title = Column(String)
    doi = Column(Integer)
    url = relationship("Link")
    projects = relationship("Project", secondary="project_publication_join_table")


class Link(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "links"
    url = Column(String)


class Funder(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "funders"
    grant_id = Column(String)
    organization = Column(String)
    grant_title = Column(String)
    projects = relationship("Project", secondary="project_funder_join_table")


###############################################################
class AccessionTypeEnum(enum.Enum):
    pass


class Accession(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "accessions"
    type = Column(Enum(AccessionTypeEnum))
    id = Column(String)


class Ontology(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "ontologies"
    text = Column(String)
    ontology = Column(String)
    ontology_label = Column(String)


class AnnotationTypeEnum(enum.Enum):
    pass


class AnnotationSourceEnum(enum.Enum):
    pass


class Annotation(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "annotations"
    type = Column(Enum(AnnotationTypeEnum))
    id = Column(String)
    source = Column(Enum(AnnotationSourceEnum))
    name = Column(String)


# Biomaterials ##############################################################
class AutolysisScoreEnum(enum.Enum):
    pass


class StateOfSpecimen(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "state_of_specimens"
    autolysis_score = Column(Enum(AutolysisScoreEnum))
    images = relationship("File", secondary="specimen_file_join_table")


class SpecimenFileJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "specimen_file_join_table"
    state_of_specimen = relationship(StateOfSpecimen)
    file = relationship("File")


class StorageMethodEnum(enum.Enum):
    pass


class PreservationMethodEnum(enum.Enum):
    pass


class PreservationStorage(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "preservation_storage"
    storage_method = Column(Enum(StorageMethodEnum))
    storage_time = Column(Integer)
    storage_time_unit = relationship(Ontology)
    preservation_method = Column(Enum(PreservationMethodEnum))


class NutritionalStateEnum(enum.Enum):
    pass


class MedicalHistory(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "medical_histories"
    alcohol_history = Column(String)
    medication = Column(String)
    smoking_history = Column(String)
    nutritional_state = Column(Enum(NutritionalStateEnum))
    test_results = Column(String)
    treatment = Column(String)


# TODO QX - Best way to model families?
class FamilialRelationship(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "familial_relationships"
    parents = relationship("DonorOrganism", secondary="donor_parent_join_table")
    children = relationship("DonorOrganism", secondary="donor_child_join_table")
    siblings = relationship("DonorOrganism", secondary="donor_sibling_join_table")


class CauseOfDeath(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "causes_of_death"
    cause_of_death = Column(String)
    cold_perfused = Column(Boolean)
    days_on_ventilator = Column(Integer)
    hardy_scale = Column(Integer)
    time_of_death = Column(DateTime)


class PlateBasedSequencing(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "plate_based_sequencing"
    plate_label = Column(String)
    well_label = Column(String)
    well_quality = Column(String)


class GrowthCondition(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "growth_conditions"
    passage_number = Column(Integer)
    growth_medium = Column(String)
    culture_environment = Column(String)


class CellMorphology(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "cell_morphologies"
    cell_morphology = Column(String)
    cell_size = Column(Integer)
    cell_size_unit = relationship(Ontology)
    percent_cell_viability = Column(Integer)
    cell_viability_method = Column(String)
    cell_viability_result = Column(String)
    percent_necrosis = Column(Integer)


class TimeCourse(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "time_courses"
    value = Column(String)
    unit = relationship(Ontology)
    relevance = Column(String)


# Protocols ###################################################################################3
class TenX(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "ten_x"
    fastq_method = Column(String)
    fastq_method_version = Column(String)
    pooled_channels = Column(Integer)
    drop_uniformity = Column(Boolean)


class BarcodeReadEnum(enum.Enum):
    pass


class Barcode(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "barcodes"
    barcode_offset = Column(Integer)
    barcode_length = Column(Integer)
    barcode_read = Column(Enum(BarcodeReadEnum))
    white_list_file = Column(String)


class PurchasedReagent(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "purchased_reagents"
    retail_name = Column(String)
    catalog_number = Column(String)
    manufacturer = Column(String)
    lot_number = Column(String)
    expiry_date = Column(DateTime)
    kit_titer = Column(String)


# processes #########
class Task(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "tasks"
    name = Column(String)
    start_time = Column(DateTime)
    stop_time = Column(DateTime)
    disk_size = Column(String)
    docker_image = Column(String)
    cpus = Column(Integer)
    memory = Column(String)
    zone = Column(String)
    log_err = Column(String)
    log_out = Column(String)


class Parameter(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "parameters"
    name = Column(String)
    value = Column(String)
    checksum = Column(String)
