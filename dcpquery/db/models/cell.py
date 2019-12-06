import enum

from sqlalchemy import Column, String, Integer, Boolean, Enum
from sqlalchemy.orm import relationship

from dcpquery.db.models import SQLAlchemyBase
from dcpquery.db.models.base import DCPModelMixin
from dcpquery.db.models.biomaterial import CellSuspension

from dcpquery.db.models.modules import Barcode, Ontology


class Cell(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "cells"
    cell_suspension = relationship(CellSuspension)  # not sure if actually necessary bc can walk graph
    sequence_file = relationship("SequenceFile")
    barcode = relationship(Barcode)  # String in matrix service?
    genes_detected = Column(Integer)
    total_umis = Column(Integer)
    empty_drops_is_cell = Column(Boolean)
    features = relationship("Feature", secondary="expressions")


class ExpressionTypeEnum(enum.Enum):
    pass


class Expression(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "expressions"
    cell = relationship(Cell)
    feature = relationship("Feature")
    expr_type = Column(Enum(ExpressionTypeEnum))
    expr_value = Column(Integer)


class FeatureTypeEnum(enum.Enum):
    pass


class Feature(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "features"
    name = Column(String)
    type = Column(Enum(FeatureTypeEnum))
    chromosome = Column(Integer)
    feature_start = Column(String)
    feature_end = Column(String)
    is_gene = Column(Boolean)
    genus_species = relationship(Ontology)
