import enum

from sqlalchemy import String, Column, Enum, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from dcpquery.db.models import SQLAlchemyBase
from dcpquery.db.models.base import DCPModelMixin
from dcpquery.db.models.modules import Ontology, Accession
from dcpquery.db.models.process import Process
from dist.deployment.psycopg2.extensions import JSONB


class DCPFile(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "files"
    # id = Column(String, primary_key=True)
    discriminator = Column('type', String(50))
    name = Column(String)
    format = Column(String)
    content_description = relationship(Ontology, secondary="file_ontology_join_table")
    checksum = Column(String)
    file_description = Column(String)
    body = Column(MutableDict.as_mutable(JSONB))
    processes = relationship(Process, secondary="process_edges")
    __mapper_args__ = {'polymorphic_on': discriminator}


class FileOntologyJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "file_ontology_join_table"
    file = relationship(File)
    ontology = relationship(Ontology)


class ReadIndexEnum(enum.Enum):
    pass


class SequenceFile(DCPFile, SQLAlchemyBase):
    __tablename__ = "sequence_file"
    id = Column(UUID, ForeignKey('files.uuid'), primary_key=True)
    read_index = Column(Enum(ReadIndexEnum))
    lane_index = Column(Integer)
    read_length = Column(Integer)
    libary_prep_id = Column(String)
    accessions = relationship(Accession, secondary="sequence_file_accession_join_table")
    __mapper_args__ = {'polymorphic_identity': 'sequence_file'}


class SequenceFileAccessionJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "sequence_file_accession_join_table"
    accession = relationship(Accession)
    sequence_file = relationship(SequenceFile)
