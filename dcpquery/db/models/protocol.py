import enum

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from dcpquery.db.models import SQLAlchemyBase
from dcpquery.db.models.base import DCPModelMixin
from dcpquery.db.models.modules import PurchasedReagent, Ontology, TenX, Barcode


class Protocol(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "protocols"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    discriminator = Column('type', String(50))
    protocol_id = Column(String)
    name = Column(String)
    description = Column(String)
    publication_doi = Column(String)
    protocols_io_doi = Column(String)
    body = Column(MutableDict.as_mutable(JSONB))
    method = relationship("Ontology")
    method_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    reagents = relationship("PurchasedReagent", secondary="protocol_reagent_join_table")
    processes = relationship("Process", secondary="process_protocol_join_table")
    __mapper_args__ = {'polymorphic_on': discriminator}


class ProtocolReagentJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "protocol_reagent_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    protocol_uuid = Column(UUID, ForeignKey('protocols.uuid'), primary_key=True)
    reagent_uuid = Column(UUID, ForeignKey('reagents.uuid'), primary_key=True)
    protocol = relationship(Protocol, foreign_keys=[protocol_uuid])
    reagent = relationship(PurchasedReagent, foreign_keys=[reagent_uuid])


class DifferentiationProtocol(Protocol, SQLAlchemyBase):
    __tablename__ = "differentiation_protocol"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    id = Column(UUID, ForeignKey('protocols.uuid'), primary_key=True)
    media = Column(String)
    small_molecules = Column(String)
    target_pathway = Column(String)
    validation_method = Column(String)
    validation_result = Column(String)
    target_cell_yield = Column(Integer)
    __mapper_args__ = {'polymorphic_identity': 'differentiation_protocol'}


class IPSCInductionProtocol(Protocol, SQLAlchemyBase):
    __tablename__ = "ipsc_induction_protocols"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    id = Column(UUID, ForeignKey('protocols.uuid'), primary_key=True)
    reprogramming_factors = Column(String)
    pluripotency_test = Column(String)
    percent_pluripotency = Column(Integer)
    ipsc_induction_kit_uuid = Column(UUID, ForeignKey('reagents.uuid'))
    ipsc_induction_kit = relationship(PurchasedReagent, foreign_keys=[ipsc_induction_kit_uuid])
    # pluripotency_vector_removed = Column(Enum(VectorRemovalEnum))
    __mapper_args__ = {'polymorphic_identity': 'ipsc_induction_protocol'}


class EndBiasEnum(enum.Enum):
    A3PT: "3 prime tag"
    A3PEB = "3 prime end bias"
    A5PT = "5 prime tag"
    A5PEB = "5 prime end bias"
    FL = "full length"


class LibraryPreparationProtocol(Protocol, SQLAlchemyBase):
    __tablename__ = "library_prep_protocols"
    id = Column(UUID, ForeignKey('protocols.uuid'), primary_key=True)
    nucleic_acid_source = Column(String)
    end_bias = Column(String)
    strand = Column(String)
    primer = Column(String)
    spike_in_dilution = Column(Integer)
    nominal_length = Column(Integer)
    nominal_sdev = Column(Integer)
    cell_barcode_uuid = Column(UUID, ForeignKey('barcodes.uuid'))
    cell_barcode = relationship(Barcode, foreign_keys=[cell_barcode_uuid])
    umi_barcode_uuid = Column(UUID, ForeignKey('barcodes.uuid'))
    umi_barcode = relationship(Barcode, foreign_keys=[umi_barcode_uuid])
    library_construction_kit_uuid = Column(UUID, ForeignKey('reagents.uuid'))
    library_construction_kit = relationship(PurchasedReagent, foreign_keys=[library_construction_kit_uuid])
    nucleic_acid_conversion_kit_uuid = Column(UUID, ForeignKey('reagents.uuid'))
    nucleic_acid_conversion_kit = relationship(PurchasedReagent, foreign_keys=[nucleic_acid_conversion_kit_uuid])
    spike_in_kit_uuid = Column(UUID, ForeignKey('reagents.uuid'))
    spike_in_kit = relationship(PurchasedReagent, foreign_keys=[spike_in_kit_uuid])
    cdna_library_amplification_method_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    cdna_library_amplification_method = relationship(Ontology, foreign_keys=[cdna_library_amplification_method_uuid])
    library_preamplification_method_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    library_preamplification_method = relationship(Ontology, foreign_keys=[library_preamplification_method_uuid])
    library_construction_method_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    library_construction_method = relationship(Ontology, foreign_keys=[library_construction_method_uuid])
    __mapper_args__ = {'polymorphic_identity': 'library_prep_protocol'}


class EnrichmentProtocol(Protocol, SQLAlchemyBase):
    __tablename__ = "enrichment_protocols"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    id = Column(UUID, ForeignKey('protocols.uuid'), primary_key=True)
    markers = Column(String)
    minimum_size = Column(Integer)
    maximum_size = Column(Integer)
    __mapper_args__ = {'polymorphic_identity': 'enrichment_protocol'}


class SequencingProtocol(Protocol, SQLAlchemyBase):
    __tablename__ = "sequencing_protocols"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    id = Column(UUID, ForeignKey('protocols.uuid'), primary_key=True)
    local_machine_name = Column(String)
    paired_end = Column(Boolean)
    ten_x = relationship(TenX)
    ten_x_uuid = Column(UUID, ForeignKey('ten_x.uuid'))
    instrument_manufacturer_model_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    instrument_manufacturer_model = relationship(Ontology, foreign_keys=[instrument_manufacturer_model_uuid])
    __mapper_args__ = {'polymorphic_identity': 'sequencing_protocol'}


class AnalysisProtocol(Protocol, SQLAlchemyBase):
    __tablename__ = "analysis_protocols"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    id = Column(UUID, ForeignKey('protocols.uuid'), primary_key=True)
    computational_method = Column(String)
    type_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    type = relationship(Ontology, foreign_keys=[type_uuid])
    __mapper_args__ = {'polymorphic_identity': 'analysis_protocol'}
