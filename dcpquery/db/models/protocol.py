import enum

from sqlalchemy import Column, String, Boolean, Integer, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from dcpquery.db.models import SQLAlchemyBase
from dcpquery.db.models.base import DCPModelMixin
from dcpquery.db.models.modules import PurchasedReagent, Ontology, TenX, Barcode


class Protocol(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "protocols"
    discriminator = Column('type', String(50))
    body = Column(MutableDict.as_mutable(JSONB))
    name = Column(String)
    description = Column(String)
    publication_doi = Column(String)
    protocols_io_doi = Column(String)
    reagents = relationship("PurchasedReagent", secondary="protocol_reagent_join_table")
    processes = relationship("Process", secondary="process_protocol_join_table")
    __mapper_args__ = {'polymorphic_on': discriminator}


class ProtocolReagentJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "protocol_reagent_join_table"
    protocol = relationship(Protocol)
    reagent = relationship(PurchasedReagent)


class DifferentiationProtocol(Protocol, SQLAlchemyBase):
    __tablename__ = "differentiation_protocol"
    id = Column(UUID, ForeignKey('protocols.uuid'), primary_key=True)
    media = Column(String)
    small_molecules = Column(String)
    target_cell_yield = Column(Integer)
    target_pathway = Column(String)
    validation_method = Column(String)
    validation_result = Column(String)
    __mapper_args__ = {'polymorphic_identity': 'differentiation_protocol'}


class VectorRemovalEnum(enum.Enum):
    pass


class IPSCInductionProtocol(Protocol, SQLAlchemyBase):
    __tablename__ = "ipsc_induction_protocols"
    id = Column(UUID, ForeignKey('protocols.uuid'), primary_key=True)
    method = Column(String)  ## whyyyy
    reprogramming_factors = Column(String)
    ipsc_induction_kit = relationship(PurchasedReagent)
    pluripotency_test = Column(String)
    percent_pluripotency = Column(Integer)
    pluripotency_vector_removed = Column(Enum(VectorRemovalEnum))
    __mapper_args__ = {'polymorphic_identity': 'ipsc_induction_protocol'}


class NucleicAcidSourceEnum(enum.Enum):
    pass


class EndBiasEnum(enum.Enum):
    pass


class LibraryPreparationProtocol(Protocol, SQLAlchemyBase):
    __tablename__ = "library_prep_protocols"
    id = Column(UUID, ForeignKey('protocols.uuid'), primary_key=True)
    library_construction_methoc = relationship(Ontology)
    nucleic_acid_source = Column(Enum(NucleicAcidSourceEnum))
    end_bias = Column(Enum(EndBiasEnum))
    strand = Column(String)
    cell_barcode = relationship(Barcode)
    umi_barcode = relationship(Barcode)
    primer = Column(String)
    library_preamplification_method = relationship(Ontology)
    cdna_library_amplification_method = relationship(Ontology)
    nominal_length = Column(Integer)
    nominal_sdev = Column(Integer)
    library_construction_kit = relationship(PurchasedReagent)
    nucleic_acid_conversion_kit = relationship(PurchasedReagent)
    spike_in_kit = relationship(PurchasedReagent)
    spike_in_dilution = Column(Integer)
    __mapper_args__ = {'polymorphic_identity': 'library_prep_protocol'}


class EnrichmentProtocol(Protocol, SQLAlchemyBase):
    __tablename__ = "enrichment_protocols"
    id = Column(UUID, ForeignKey('protocols.uuid'), primary_key=True)
    markers = Column(String)
    minimum_size = Column(Integer)
    maximum_size = Column(Integer)
    __mapper_args__ = {'polymorphic_identity': 'enrichment_protocol'}


class SequencingProtocol(Protocol, SQLAlchemyBase):
    __tablename__ = "sequencing_protocols"
    id = Column(UUID, ForeignKey('protocols.uuid'), primary_key=True)
    instrument_manufacturer_model = relationship(Ontology)
    paired_end = Column(Boolean)
    ten_x = relationship(TenX)
    local_machine_name = Column(String)
    __mapper_args__ = {'polymorphic_identity': 'sequencing_protocol'}


class AnalysisProtocol(Protocol, SQLAlchemyBase):
    __tablename__ = "analysis_protocols"
    id = Column(UUID, ForeignKey('protocols.uuid'), primary_key=True)
    computational_method = Column(String)
    type = relationship(Ontology)
    __mapper_args__ = {'polymorphic_identity': 'analysis_protocol'}
