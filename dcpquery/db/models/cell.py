import logging
from uuid import uuid4

from sqlalchemy import Column, String, Integer, Boolean, Enum, ForeignKey
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

    cellkey = Column(String)
    genes_detected = Column(Integer)
    total_umis = Column(Integer)
    empty_drops_is_cell = Column(Boolean)
    barcode_uuid = Column(UUID(as_uuid=True), ForeignKey('barcodes.uuid'))
    barcode = Column(String)  # String in matrix service?
    file_uuid = Column(UUID(as_uuid=True), ForeignKey('files.uuid'))
    file = relationship("DCPFile")
    cell_suspension_uuid = Column(UUID(as_uuid=True), ForeignKey('cell_suspensions.uuid'))
    cell_suspension = relationship(CellSuspension)  # not sure if actually necessary bc can walk graph
    features = relationship("Feature", secondary="expressions")

    @classmethod
    def get(cls, cellkey):
        return config.db_session.query(cls).filter(cls.cellkey == cellkey).one_or_none()

    @classmethod
    def create(cls, cellkey=None, uuid=None, **kw):
        if not uuid:
            uuid = str(uuid4())
        row = cls(uuid=uuid, cellkey=cellkey ** kw)
        try:
            config.db_session.add(row)
        except Exception as e:
            logger.info(f"Issue {e} inserting {cls} {kw}")
            config.db_session.rollback()
            pass
        return row

    @classmethod
    def get_or_create(cls, cellkey, **kw):
        existing_object = cls.get(cellkey)
        if existing_object:
            return existing_object
        try:
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
    cell_uuid = Column(UUID(as_uuid=True), ForeignKey('cells.uuid'), primary_key=True)
    feature_uuid = Column(UUID(as_uuid=True), ForeignKey('features.uuid'), primary_key=True)
    cell = relationship(Cell, foreign_keys=[cell_uuid])
    feature = relationship("Feature", foreign_keys=[feature_uuid])


class Feature(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "features"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    id = Column(String, primary_key=True, )
    type = Column(String)  # todo make an enum?
    name = Column(String)
    feature_start = Column(String)
    feature_end = Column(String)
    chromosome = Column(Integer)
    is_gene = Column(Boolean)
    genus_species_id = Column(String, ForeignKey('ontologies.ontology'))
    genus_species = relationship(Ontology)
    accession_id = Column(String, ForeignKey('accessions.id'))
    accession = relationship(Accession)
    cells = relationship(Cell, secondary="expressions")
