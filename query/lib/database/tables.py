import datetime

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Table, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


# bundles_files_association_table = Table('bundles_files', Base.metadata,
#                                         Column('bundle_fqid', String, ForeignKey('bundle.fqid')),
#                                         Column('file_fqid', String, ForeignKey('file.fqid'))
#                                         )


class Bundles(Base):
    __tablename__ = 'bundle'
    fqid = Column(String, primary_key=True)
    uuid = Column(UUID, nullable=False)
    version = Column(DateTime, nullable=False)
    manifest = Column(JSONB)
    files = relationship("Files", secondary='bundle_file_link')


class SchemaTypes(Base):
    __tablename__ = 'schema_type'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    files = relationship("Files", back_populates='schema_type')


class Files(Base):
    __tablename__ = 'file'
    fqid = Column(String, primary_key=True)
    uuid = Column(UUID, nullable=False)
    version = Column(DateTime, nullable=False)
    name = Column(String, nullable=False)
    json = Column(JSONB)
    schema_type_id = Column(Integer, ForeignKey('schema_type.id'))
    schema_type = relationship("SchemaTypes", back_populates='files')
    bundles = relationship("Bundles", secondary='bundle_file_link')


class BundlesFilesLink(Base):
    __tablename__ = 'bundle_file_link'
    file_fqid = Column(String, ForeignKey('file.fqid'), primary_key=True)
    bundle_fqid = Column(String, ForeignKey('bundle.fqid'), primary_key=True)
    file = relationship(Files)
    bundle = relationship(Bundles)


class JobStatusEnum(enum.Enum):
    CREATED = 'CREATED'
    PROCESSING = 'PROCESSING'
    COMPLETE = 'COMPLETE'
    FAILED = 'FAILED'


class JobStatus(Base):
    __tablename__ = 'job_status'
    id = Column(UUID, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(Enum(JobStatusEnum))
