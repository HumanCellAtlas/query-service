import datetime

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Table, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

bundles_files_association_table = Table('bundles_files', Base.metadata,
                                        Column('bundle_fqid', String, ForeignKey('bundle.fqid')),
                                        Column('file_fqid', String, ForeignKey('file.fqid'))
                                        )


class Bundle(Base):
    __tablename__ = 'bundle'
    fqid = Column(String, primary_key=True, unique=True)
    uuid = Column(UUID, nullable=False)
    version = Column(DateTime, nullable=False)
    manifest = Column(JSONB)
    files = relationship("File", secondary=bundles_files_association_table, back_populates='bundles')


class SchemaType(Base):
    __tablename__ = 'schema_type'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    files = relationship("File", back_populates='schema_type')


class File(Base):
    __tablename__ = 'file'
    fqid = Column(String, nullable=False, primary_key=True)
    uuid = Column(UUID, nullable=False)
    version = Column(DateTime, nullable=False)
    name = Column(String, nullable=False)
    schema_type_id = Column(Integer, ForeignKey('schema_type.id'))
    schema_type = relationship("SchemaType", back_populates='files')
    bundles = relationship("Bundle", secondary=bundles_files_association_table, back_populates='files')


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
