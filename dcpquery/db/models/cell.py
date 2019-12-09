from sqlalchemy import Column, String, Integer, Boolean, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from dcpquery.db.models import SQLAlchemyBase
from dcpquery.db.models.base import DCPModelMixin
from dcpquery.db.models.biomaterial import CellSuspension

from dcpquery.db.models.modules import Barcode, Ontology


class Cell(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "cells"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    genes_detected = Column(Integer)
    total_umis = Column(Integer)
    empty_drops_is_cell = Column(Boolean)
    barcode_uuid = Column(UUID(as_uuid=True), ForeignKey('barcodes.uuid'))
    barcode = relationship(Barcode)  # String in matrix service?
    sequence_file_uuid = Column(UUID(as_uuid=True), ForeignKey('sequence_files.uuid'))
    sequence_file = relationship("SequenceFile")
    cell_suspension_uuid = Column(UUID(as_uuid=True), ForeignKey('cell_suspensions.uuid'))
    cell_suspension = relationship(CellSuspension)  # not sure if actually necessary bc can walk graph
    features = relationship("Feature", secondary="expressions")

# Join Table but keeping here for now
class Expression(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "expressions"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    expr_type = Column(String)  # todo make an enmu?
    expr_value = Column(Integer)
    cell_uuid = Column(UUID(as_uuid=True), ForeignKey('cells.uuid'), primary_key=True)
    feature_uuid = Column(UUID(as_uuid=True), ForeignKey('features.uuid'), primary_key=True)
    cell = relationship(Cell, foreign_keys=[cell_uuid])
    feature = relationship("Feature", foreign_keys=[feature_uuid])


class Feature(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "features"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    type = Column(String) # todo make an enum?
    name = Column(String)
    feature_start = Column(String)
    feature_end = Column(String)
    chromosome = Column(Integer)
    is_gene = Column(Boolean)
    genus_species_id = Column(String, ForeignKey('ontologies.ontology'))
    genus_species = relationship(Ontology)
    cells = relationship(Cell, secondary="expressions")
