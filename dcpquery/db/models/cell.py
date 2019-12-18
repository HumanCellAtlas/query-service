import logging
from uuid import uuid4

from sqlalchemy import Column, String, Integer, Boolean, Enum, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from dcpquery import config
from dcpquery.db.models import SQLAlchemyBase
from dcpquery.db.models.base import DCPModelMixin
from dcpquery.db.models.biomaterial import CellSuspension
from dcpquery.db.models.enums import ExpressionTypeEnum

from dcpquery.db.models.modules import Barcode, Ontology, Accession

logger = logging.getLogger(__name__)


class Cell(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "cells"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return self.cellkey

    cellkey = Column(String, primary_key=True, index=True, unique=True)
    genes_detected = Column(Integer)
    total_umis = Column(Float)
    empty_drops_is_cell = Column(Boolean)
    barcode = Column(String)  # String in matrix service?
    file_uuid = Column(UUID(as_uuid=True))  # todo join when all loaded
    # file = relationship("DCPFile")
    cell_suspension_uuid = Column(UUID(as_uuid=True))  # todo join when matrices and files loaded
    # cell_suspension = relationship(CellSuspension)  # not sure if actually necessary bc can walk graph
    features = relationship("Feature", secondary="expressions")

    @classmethod
    def get(cls, cellkey):
        return config.db_session.query(cls).filter(cls.cellkey == cellkey).one_or_none()

    @classmethod
    def create(cls, cellkey=None, uuid=None, **kw):
        if not uuid:
            uuid = str(uuid4())
        row = cls(uuid=uuid, cellkey=cellkey, **kw)
        try:
            config.db_session.add(row)
        except Exception as e:
            logger.info(f"Issue {e} inserting {cls} {kw}")
            config.db_session.rollback()
            pass
        return row

    @classmethod
    def get_or_create(cls, cellkey, **kw):
        try:
            existing_object = cls.get(cellkey=cellkey)
            if existing_object:
                return existing_object
            return cls.create(cellkey=cellkey, **kw)
        except Exception as e:
            logger.info(f"SOMETHING WENT WRONG: CLS: {cls}, exception: {e} {kw}")
            config.db_session.rollback()
            pass


# Join Table but keeping here for now
class Expression(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "expressions"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    expr_type = Column(Enum(ExpressionTypeEnum))  # todo make an enmu?
    expr_value = Column(Integer)
    cell_key = Column(String, ForeignKey('cells.cellkey'), primary_key=True)
    feature_accession_id = Column(String, ForeignKey('features.accession_id'), primary_key=True)
    cell = relationship(Cell, foreign_keys=[cell_key])
    feature = relationship("Feature", foreign_keys=[feature_accession_id])

    @classmethod
    def create(cls, uuid=None, **kw):
        if not uuid:
                uuid = str(uuid4())
        row = cls(uuid=uuid, **kw)
        try:
            config.db_session.add(row)
        except Exception as e:
            logger.info(f"Issue {e} inserting expression, {uuid}, {kw}")
            config.db_session.rollback()
            pass
        return row

# just call gene?
class Feature(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "features"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return self.accession_id

    id = Column(String)
    type = Column(String)  # todo make an enum?
    name = Column(String)
    barcode = Column(String)  # todo what is this?
    feature_start = Column(String)
    feature_end = Column(String)
    chromosome = Column(String)
    is_gene = Column(Boolean)
    genus_species_id = Column(String, ForeignKey('ontologies.ontology'))
    genus_species = relationship(Ontology)
    # todo make primary key at next db-init
    accession_id = Column(String, ForeignKey('accessions.id'), index=True, primary_key=True, unique=True)
    accession = relationship(Accession)
    cells = relationship(Cell, secondary="expressions")

    @classmethod
    def get(cls, accession_id):
        return config.db_session.query(cls).filter(cls.accession_id == accession_id).one_or_none()

    @classmethod
    def create(cls, accession_id=None, uuid=None, **kw):
        if not uuid:
            uuid = str(uuid4())
        row = cls(uuid=uuid, accession_id=accession_id, **kw)
        try:
            config.db_session.add(row)
        except Exception as e:
            logger.info(f"Issue {e} inserting {cls} {kw}")
            config.db_session.rollback()
            pass
        return row

    @classmethod
    def get_or_create(cls, accession_id, **kw):
        existing_object = cls.get(accession_id)
        if existing_object:
            return existing_object
        try:
            return cls.create(accession_id=accession_id, **kw)
        except Exception as e:
            logger.info(f"SOMETHING WENT WRONG: CLS: {cls}, exception: {e} {kw}")
            config.db_session.rollback()
            pass
