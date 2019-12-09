from sqlalchemy import String, Column, Enum, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from dcpquery.db.models import SQLAlchemyBase
from dcpquery.db.models.base import DCPModelMixin
from dcpquery.db.models.enums import ReadIndexEnum
from dcpquery.db.models.modules import Ontology, Accession
from dcpquery.db.models.process import Process


class DCPFile(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "files"

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

    discriminator = Column('type', String(50))
    name = Column(String)
    format = Column(String)
    checksum = Column(String)
    file_description = Column(String)
    body = Column(MutableDict.as_mutable(JSONB))
    processes = relationship(Process, secondary="process_file_join_table")
    content_description = relationship(Ontology, secondary="file_ontology_join_table")
    __mapper_args__ = {'polymorphic_on': discriminator}


class SequenceFile(DCPFile, SQLAlchemyBase):
    __tablename__ = "sequence_files"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    uuid = Column(UUID(as_uuid=True), ForeignKey('files.uuid'), primary_key=True)
    discriminator = 'sequence_file'
    read_index = Column(Enum(ReadIndexEnum))
    libary_prep_id = Column(String)
    lane_index = Column(Integer)
    read_length = Column(Integer)
    accessions = relationship(Accession, secondary="sequence_file_accession_join_table")
    __mapper_args__ = {'polymorphic_identity': 'sequence_file'}


