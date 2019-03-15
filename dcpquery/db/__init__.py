"""
This module provides a SQLAlchemy-based database schema for the DCP Query Service.
"""

import os, sys, argparse, json, logging, typing

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Table, Enum, exc as sqlalchemy_exceptions
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, sessionmaker

from .. import config
from ..exceptions import DCPQueryError, QueryTimeoutError

logger = logging.getLogger(__name__)

SQLAlchemyBase = declarative_base()  # type: typing.Any


class DCPQueryModelHelper:
    def __init__(self, *args, **kwargs):
        if "fqid" in kwargs:
            assert "uuid" not in kwargs and "version" not in kwargs
            kwargs["uuid"], kwargs["version"] = kwargs["fqid"].split(".", 1)
        else:
            assert "fqid" not in kwargs
            kwargs["fqid"] = kwargs["uuid"] + "." + kwargs["version"]
        super().__init__(*args, **kwargs)
        self.foo = 1

    def bar(self):
        return self.foo


class Bundle(DCPQueryModelHelper, SQLAlchemyBase):
    __tablename__ = 'bundles'
    fqid = Column(String, primary_key=True, unique=True, nullable=False)
    uuid = Column(UUID, nullable=False)
    version = Column(DateTime, nullable=False)
    manifest = Column(JSONB)
    aggregate_metadata = Column(JSONB)
    files = relationship("File", secondary='bundle_file_links')  # , back_populates="bundles")


class SchemaType(SQLAlchemyBase):
    __tablename__ = 'schema_types'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    files = relationship("File", back_populates='schema_type')


class File(DCPQueryModelHelper, SQLAlchemyBase):
    __tablename__ = 'files'
    fqid = Column(String, primary_key=True, unique=True, nullable=False)
    uuid = Column(UUID, nullable=False)
    version = Column(DateTime, nullable=False)
    schema_type_id = Column(Integer, ForeignKey("schema_types.id"))
    schema_type = relationship("SchemaType", back_populates="files")
    body = Column(JSONB)
    content_type = Column(String)
    size = Column(Integer)
    # bundles = relationship("Bundle", secondary=BundleFileLink, back_populates="files")


class BundleFileLink(SQLAlchemyBase):
    __tablename__ = 'bundle_file_links'
    bundle_fqid = Column(String, ForeignKey('bundles.fqid'), primary_key=True)
    file_fqid = Column(String, ForeignKey('files.fqid'), primary_key=True)
    bundle = relationship(Bundle)
    file = relationship(File)
    name = Column(String, nullable=False)


def init_database(db, dry_run=True, action="init"):
    assert db in {"local", "remote"}
    from sqlalchemy_utils import database_exists, create_database

    if db == "remote":
        config.local_mode = False

    logger.info("Initializing database at %s", repr(config.db.url))

    if not database_exists(config.db.url):
        logger.info("Creating database")
        create_database(config.db.url)

    logger.info("Initializing database")
    if dry_run:
        config._db_engine_params.update(strategy="mock", executor=lambda sql, *args, **kwargs: print(sql))
    SQLAlchemyBase.metadata.create_all(config.db)


def run_query(query, timeout_seconds=20):
    # TODO: pagination of results
    # Warning: timeout_seconds is only effective once at startup when db is not yet initialized
    if config.db_statement_timeout_seconds != timeout_seconds:
        config.db_statement_timeout_seconds = timeout_seconds
    try:
        return config.db_session.execute(query)
    except sqlalchemy_exceptions.ProgrammingError as e:
        raise DCPQueryError(title=e.orig.pgerror, detail={"pgcode": e.orig.pgcode})
    except sqlalchemy_exceptions.OperationalError as e:
        if "canceling statement due to statement timeout" in str(e):
            raise QueryTimeoutError(title=e.orig.pgerror, detail={"pgcode": e.orig.pgcode})
        else:
            raise
