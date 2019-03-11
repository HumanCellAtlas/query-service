"""
This module provides a SQLAlchemy-based database schema for the DCP Query Service.
"""

import os, sys, argparse, json, logging

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Table, Enum, exc as sqlalchemy_exceptions
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, sessionmaker

from .. import config
from ..exceptions import DCPQueryError, QueryTimeoutError

logger = logging.getLogger(__name__)

Base = declarative_base()


class BundlesFiles(Base):
    __tablename__ = 'bundles_files'
    id = Column(Integer, primary_key=True)
    bundle_fqid = Column(String, ForeignKey('bundle.fqid'))
    file_fqid = Column(String, ForeignKey('file.fqid'))
    name = Column(String, nullable=False)


class Bundle(Base):
    __tablename__ = 'bundle'
    fqid = Column(String, primary_key=True, unique=True, nullable=False)
    uuid = Column(UUID, nullable=False)
    version = Column(DateTime, nullable=False)
    manifest = Column(JSONB)
    files = relationship("File", secondary=BundlesFiles, back_populates="bundles")


class SchemaType(Base):
    __tablename__ = 'schema_type'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    files = relationship("File", back_populates='schema_type')


class File(Base):
    __tablename__ = 'file'
    fqid = Column(String, primary_key=True, unique=True, nullable=False)
    uuid = Column(UUID, nullable=False)
    version = Column(DateTime, nullable=False)
    schema_type_id = Column(Integer, ForeignKey("schema_type.id"))
    schema_type = relationship("SchemaType", back_populates="files")
    bundles = relationship("Bundle", secondary=BundlesFiles, back_populates="files")


def init_database(action, db, dry_run):
    from sqlalchemy_utils import database_exists, create_database

    if db == "remote":
        config.local_mode = False

    logger.info("Initializing database at %s", repr(config.db.url))

    if not database_exists(config.db.url):
        logger.info("Creating database")
        create_database(config.db.url)

    logger.info("Initializing database")
    if dry_run:
        config._engine_params.update(strategy="mock", executor=lambda sql, *args, **kwargs: print(sql))
    Base.metadata.create_all(config.db)


def run_query(query, timeout_seconds=20):
    # TODO: pagination of results
    # Warning: timeout_seconds is only effective once at startup when db is not yet initialized
    if config.db_statement_timeout != timeout_seconds:
        config.db_statement_timeout = timeout_seconds
    try:
        return config.db_session.execute(query)
    except sqlalchemy_exceptions.ProgrammingError as e:
        raise DCPQueryError(title=e.orig.pgerror, detail={"pgcode": e.orig.pgcode})
    except sqlalchemy_exceptions.OperationalError as e:
        if "canceling statement due to statement timeout" in str(e):
            raise QueryTimeoutError(title=e.orig.pgerror, detail={"pgcode": e.orig.pgcode})
        else:
            raise
