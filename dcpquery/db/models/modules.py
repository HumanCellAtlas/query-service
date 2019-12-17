import enum
import logging
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, Integer, Enum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from dcpquery import config
from dcpquery.db.models import SQLAlchemyBase
from dcpquery.db.models.admin import User
from dcpquery.db.models.base import DCPModelMixin
from dcpquery.db.models.enums import (AccessionTypeEnum, StorageMethodEnum,
                                      PreservationMethodEnum, NutritionalStateEnum, BarcodeReadEnum, WellQualityEnum,
                                      AnnotationTypeEnum, AnnotationSourceEnum)

logger = logging.getLogger(__name__)


class Contributor(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "contributors"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    institution = Column(String)  # make table or enum?
    lab = Column(String)  # make table?
    corresponding_contributor = Column(Boolean)
    project_role_id = Column(String, ForeignKey('ontologies.ontology'))
    project_role = relationship("Ontology")
    user_uuid = Column(UUID(as_uuid=True), ForeignKey('users.uuid'))
    user = relationship(User)
    projects = relationship("Project", secondary="project_contributor_join_table")


class Publication(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "publications"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return self.title

    authors = Column(String)
    # authors = relationship("User", secondary="publication_author_join_table")
    title = Column(String)
    doi = Column(String)  # todo make an int?
    url_name = Column(String, ForeignKey('urls.url'))
    url = relationship("URL_Object", foreign_keys=[url_name])
    projects = relationship("Project", secondary="project_publication_join_table")


class URL_Object(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "urls"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return self.url


    url = Column(String, unique=True, primary_key=True)

    @classmethod
    def get(cls, url):
        return config.db_session.query(cls).filter(cls.url == url).one_or_none()

    @classmethod
    def create(cls, url, **kw):
        uuid = str(uuid4())
        row = cls(url=url, uuid=uuid, **kw)
        try:
            config.db_session.add(row)
        except Exception as e:
            logger.info(f"Issue {e} inserting {cls}, {uuid}, {kw}")
            config.db_session.rollback()
            pass
        return row

    @classmethod
    def get_or_create(cls, url, **kw):
        existing_object = cls.get(url)
        if existing_object:
            return existing_object
        try:
            return cls.create(url=url, **kw)
        except Exception as e:
            logger.info(f"SOMETHING WENT WRONG: URL_Object CLS: {cls}, uuid: {uuid}, exception: {e} ")
            config.db_session.rollback()


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

    def __repr__(self):
        return self.id

    type = Column(Enum(AccessionTypeEnum))
    id = Column(String, primary_key=True, index=True, unique=True)

    @classmethod
    def get(cls, id):
        return config.db_session.query(cls).filter(cls.id == id).one_or_none()

    @classmethod
    def create(cls, id=None, uuid=None, **kw):
        if not uuid:
            uuid = str(uuid4())
        row = cls(uuid=uuid, id=id, **kw)
        try:
            config.db_session.add(row)
        except Exception as e:
            logger.info(f"Issue {e} inserting {cls}, {uuid}, {kw}")
            config.db_session.rollback()
            pass
        return row

    @classmethod
    def get_or_create(cls, id=None, **kw):
        existing_object = cls.get(id)
        if existing_object:
            return existing_object
        try:
            return cls.create(id=id, **kw)
        except Exception as e:
            logger.info(f"SOMETHING WENT WRONG: CLS: {cls}, uuid: {uuid}, exception: {e} ")
            config.db_session.rollback()


class Ontology(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "ontologies"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return self.ontology

    uuid = Column(UUID, primary_key=False)
    text = Column(String)
    ontology = Column(String, primary_key=True, index=True, unique=True, nullable=False)
    ontology_label = Column(String)
    discriminator = Column('type', String(50))
    __mapper_args__ = {'polymorphic_on': discriminator}

    @classmethod
    def get(cls, ontology):
        return config.db_session.query(cls).filter(cls.ontology == ontology).one_or_none()

    @classmethod
    def get_by_label(cls, ontology_label):
        return config.db_session.query(cls).filter(cls.ontology_label == ontology_label).one_or_none()

    @classmethod
    def create(cls, ontology=None, uuid=None, **kw):
        if not uuid:
            uuid = str(uuid4())
        row = cls(uuid=uuid, ontology=ontology, **kw)
        try:
            config.db_session.add(row)
        except Exception as e:
            logger.info(f"Issue {e} inserting {cls}, {uuid}, {kw}")
            config.db_session.rollback()
            pass
        return row

    @classmethod
    def get_or_create(cls, ontology=None, **kw):
        existing_object = cls.get(ontology)
        if existing_object:
            return existing_object
        try:
            return cls.create(ontology=ontology, **kw)
        except Exception as e:
            logger.info(f"SOMETHING WENT WRONG: CLS: {cls}, uuid: {uuid}, exception: {e} ")
            config.db_session.rollback()



class Annotation(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "annotations"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return self.id

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

    def __repr__(self):
        return self.storage_method

    storage_method = Column(Enum(StorageMethodEnum))
    preservation_method = Column(Enum(PreservationMethodEnum))
    storage_time = Column(Integer)
    storage_time_unit = relationship(Ontology)
    storage_time_unit_id = Column(String, ForeignKey('ontologies.ontology'))


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

    def __repr__(self):
        return self.cause_of_death


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
    well_quality = Column(Enum(WellQualityEnum))


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

    def __repr__(self):
        return self.cell_morphology if self.cell_morphology else 'NONE'


    cell_morphology = Column(String)
    cell_viability_method = Column(String)
    cell_viability_result = Column(String)
    cell_size = Column(String)
    percent_cell_viability = Column(Integer)
    percent_necrosis = Column(Integer)
    cell_size_unit = relationship(Ontology)
    cell_size_unit_id = Column(String, ForeignKey('ontologies.ontology'))


class TimeCourse(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "time_courses"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    value = Column(String)
    relevance = Column(String)
    unit = relationship(Ontology)
    unit_id = Column(String, ForeignKey('ontologies.ontology'))


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
    barcode_string = Column(String)

    @classmethod
    def get_by_string(cls, barcode_string):
        return config.db_session.query(cls).filter(cls.barcode_string == barcode_string).one_or_none()

    @classmethod
    def create_by_string(cls, barcode_string=None, uuid=None, **kw):
        if not uuid:
            uuid = str(uuid4())
        row = cls(uuid=uuid, barcode_string=barcode_string, **kw)
        try:
            config.db_session.add(row)
        except Exception as e:
            logger.info(f"Issue {e} inserting {cls}, {uuid}, {kw}")
            config.db_session.rollback()
            pass
        return row

    @classmethod
    def get_or_create_by_string(cls, barcode_string, **kw):
        try:
            existing_object = cls.get_by_string(barcode_string)
            if existing_object:
                return existing_object
        except Exception as e:
            print(f"what nowwww>?? {e}")
        try:
            return cls.create(barcode_string=barcode_string, **kw)
        except Exception as e:
            logger.info(f"SOMETHING WENT WRONG: CLS: {cls}, exception: {e} ")
            config.db_session.rollback()


class PurchasedReagent(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "reagents"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return self.retail_name


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

    def __unicode__(self):
        return self.name

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

    def __unicode__(self):
        return self.name

    name = Column(String)
    value = Column(String)
    checksum = Column(String)
