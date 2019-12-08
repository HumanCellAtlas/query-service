from sqlalchemy import Column, String, Boolean, Integer, Enum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from dcpquery.db.models import SQLAlchemyBase
from dcpquery.db.models.admin import User
from dcpquery.db.models.base import DCPModelMixin
from dcpquery.db.models.enums import AccessionTypeEnum, AnnotationTypeEnum, AnnotationSourceEnum, StorageMethodEnum, \
    PreservationMethodEnum, NutritionalStateEnum, BarcodeReadEnum


class Contributor(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "contributors"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    institution = Column(String)  # make table or enum?
    lab = Column(String)  # make table?
    corresponding_contributor = Column(Boolean)
    project_role_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    project_role = relationship("Ontology")
    user_uuid = Column(UUID, ForeignKey('users.uuid'))
    user = relationship(User)
    projects = relationship("Project", secondary="project_contributor_join_table")


class Publication(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "publications"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    authors = Column(String)
    # authors = relationship("User", secondary="publication_author_join_table")
    title = Column(String)
    doi = Column(Integer)
    url = relationship("Link")
    url_uuid = Column(UUID, ForeignKey('links.uuid'))
    projects = relationship("Project", secondary="project_publication_join_table")


class Link(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "links"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    url = Column(String)


class Funder(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "funders"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    grant_id = Column(String)
    organization = Column(String)
    grant_title = Column(String)
    projects = relationship("Project", secondary="project_funder_join_table")


###############################################################


class Accession(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "accessions"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    type = Column(Enum(AccessionTypeEnum))
    id = Column(String)


class Ontology(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "ontologies"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    text = Column(String)
    ontology = Column(String)
    ontology_label = Column(String)
    discriminator = Column('type', String(50))
    __mapper_args__ = {'polymorphic_on': discriminator}


class Annotation(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "annotations"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    type = Column(Enum(AnnotationTypeEnum))
    source = Column(Enum(AnnotationSourceEnum))
    id = Column(String)
    name = Column(String)


# Biomaterials ##############################################################


# class StateOfSpecimen(DCPModelMixin, SQLAlchemyBase):
#     __tablename__ = "state_of_specimens"
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#     autolysis_score = Column(Enum(AutolysisScoreEnum))
#     images = relationship("DCPFile", secondary="specimen_file_join_table")
#
#
# class SpecimenFileJoinTable(DCPModelMixin, SQLAlchemyBase):
#     __tablename__ = "specimen_file_join_table"
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#     file_uuid = Column(UUID, ForeignKey('files.uuid'), primary_key=True)
#     state_of_specimen_uuid = Column(UUID, ForeignKey('state_of_specimens.uuid'), primary_key=True)
#     state_of_specimen = relationship(StateOfSpecimen, back_populates='images')
#     file = relationship("DCPFile")


class PreservationStorage(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "preservation_storage"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    storage_method = Column(Enum(StorageMethodEnum))
    preservation_method = Column(Enum(PreservationMethodEnum))
    storage_time = Column(Integer)
    storage_time_unit = relationship(Ontology)
    storage_time_unit_uuid = Column(UUID, ForeignKey('ontologies.uuid'))


class MedicalHistory(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "medical_histories"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    nutritional_state = Column(Enum(NutritionalStateEnum))
    alcohol_history = Column(String)
    medication = Column(String)
    smoking_history = Column(String)
    test_results = Column(String)
    treatment = Column(String)


# TODO QX - Best way to model families?
class FamilialRelationship(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "familial_relationships"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    parents = Column(String)
    children = Column(String)
    siblings = Column(String)
    # parents = relationship("DonorOrganism", secondary="donor_parent_join_table")
    # children = relationship("DonorOrganism", secondary="donor_child_join_table")
    # siblings = relationship("DonorOrganism", secondary="donor_sibling_join_table")


class CauseOfDeath(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "causes_of_death"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    cause_of_death = Column(String)
    time_of_death = Column(DateTime)
    cold_perfused = Column(Boolean)
    days_on_ventilator = Column(Integer)
    hardy_scale = Column(Integer)


class PlateBasedSequencing(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "plate_based_sequencing"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    plate_label = Column(String)
    well_label = Column(String)
    well_quality = Column(String)


class GrowthCondition(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "growth_conditions"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    passage_number = Column(Integer)
    growth_medium = Column(String)
    culture_environment = Column(String)


class CellMorphology(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "cell_morphologies"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    cell_morphology = Column(String)
    cell_viability_method = Column(String)
    cell_viability_result = Column(String)
    cell_size = Column(Integer)
    percent_cell_viability = Column(Integer)
    percent_necrosis = Column(Integer)
    cell_size_unit = relationship(Ontology)
    cell_size_unit_uuid = Column(UUID, ForeignKey('ontologies.uuid'))


class TimeCourse(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "time_courses"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    value = Column(String)
    relevance = Column(String)
    unit = relationship(Ontology)
    unit_uuid = Column(UUID, ForeignKey('ontologies.uuid'))


# Protocols ###################################################################################3
class TenX(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "ten_x"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    fastq_method = Column(String)
    fastq_method_version = Column(String)
    drop_uniformity = Column(Boolean)
    pooled_channels = Column(Integer)


class Barcode(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "barcodes"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    barcode_read = Column(Enum(BarcodeReadEnum))
    white_list_file = Column(String)
    barcode_offset = Column(Integer)
    barcode_length = Column(Integer)


class PurchasedReagent(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "reagents"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    retail_name = Column(String)
    catalog_number = Column(String)
    manufacturer = Column(String)
    lot_number = Column(String)
    kit_titer = Column(String)
    expiry_date = Column(DateTime)


# processes #########
class Task(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "tasks"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    name = Column(String)
    docker_image = Column(String)
    disk_size = Column(String)
    start_time = Column(DateTime)
    stop_time = Column(DateTime)
    memory = Column(String)
    zone = Column(String)
    log_err = Column(String)
    log_out = Column(String)
    cpus = Column(Integer)


class Parameter(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "parameters"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    name = Column(String)
    value = Column(String)
    checksum = Column(String)
