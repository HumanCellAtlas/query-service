"""
This module provides a SQLAlchemy-based database schema for the DCP Query Service.
"""
import enum
import os, sys, argparse, json, logging, typing

from sqlalchemy import (Column, String, DateTime, Integer, ForeignKey, Table, Enum, exc as sqlalchemy_exceptions,
                        UniqueConstraint, BigInteger)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableDict
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


class Bundle(DCPQueryModelHelper, SQLAlchemyBase):
    __tablename__ = 'bundles'
    fqid = Column(String, primary_key=True, unique=True, nullable=False)
    uuid = Column(UUID, nullable=False)
    version = Column(DateTime, nullable=False)
    manifest = Column(MutableDict.as_mutable(JSONB))
    aggregate_metadata = Column(MutableDict.as_mutable(JSONB))
    files = relationship("File", secondary='bundle_file_links')


class DCPMetadataSchemaType(SQLAlchemyBase):
    __tablename__ = 'dcp_metadata_schema_types'
    name = Column(String, primary_key=True, nullable=False)
    files = relationship("File", back_populates='dcp_schema_type')


class File(DCPQueryModelHelper, SQLAlchemyBase):
    __tablename__ = 'files'
    fqid = Column(String, primary_key=True, unique=True, nullable=False)
    uuid = Column(UUID, nullable=False)
    version = Column(DateTime, nullable=False)
    dcp_schema_type_name = Column(String, ForeignKey("dcp_metadata_schema_types.name"))
    dcp_schema_type = relationship("DCPMetadataSchemaType", back_populates="files")
    body = Column(MutableDict.as_mutable(JSONB))
    content_type = Column(String)
    size = Column(BigInteger)
    extension = Column(String)


class BundleFileLink(SQLAlchemyBase):
    __tablename__ = 'bundle_file_links'
    bundle_fqid = Column(String, ForeignKey('bundles.fqid'), primary_key=True)
    file_fqid = Column(String, ForeignKey('files.fqid'), primary_key=True)
    bundle = relationship(Bundle)
    file = relationship(File)
    name = Column(String, nullable=False)


class ConnectionTypeEnum(enum.Enum):
    INPUT_ENTITY = 'INPUT_ENTITY'
    OUTPUT_ENTITY = 'OUTPUT_ENTITY'
    PROTOCOL_ENTITY = 'PROTOCOL_ENTITY'


class Process(SQLAlchemyBase):
    __tablename__ = 'processes'
    process_uuid = Column(UUID, primary_key=True)

    @classmethod
    def list_all_child_processes(cls, process_uuid):
        child_process_uuids = config.db_session.execute(f"SELECT * FROM get_all_children('{process_uuid}')").fetchall()
        return [str(child_process[0]) for child_process in child_process_uuids]

    @classmethod
    def list_all_parent_processes(cls, process_uuid):
        parent_process_uuids = config.db_session.execute(f"SELECT * FROM get_all_parents('{process_uuid}')").fetchall()
        return [str(parent_process[0]) for parent_process in parent_process_uuids]

    @classmethod
    def list_direct_child_processes(cls, process_uuid):
        return config.db_session.query(ProcessProcessLink).with_entities(ProcessProcessLink.child_process_uuid).filter(
            ProcessProcessLink.parent_process_uuid == process_uuid).all()

    @classmethod
    def list_direct_parent_processes(cls, process_uuid):
        return config.db_session.query(ProcessProcessLink).with_entities(ProcessProcessLink.parent_process_uuid).filter(
            ProcessProcessLink.child_process_uuid == process_uuid).all()


class ProcessFileLink(SQLAlchemyBase):
    __tablename__ = 'process_file_join_table'
    id = Column(Integer, primary_key=True)
    process_uuid = Column(UUID, ForeignKey("processes.process_uuid"))
    process_file_connection_type = Column(Enum(ConnectionTypeEnum))
    process = relationship(Process)
    file_uuid = Column(UUID)

    __table_args__ = (UniqueConstraint(
        'process_uuid', 'process_file_connection_type', 'file_uuid', name='process_file_connection_type_uc'),)

    def get_most_recent_file(self):
        return config.db_session.query(File).filter(File.uuid == self.file_uuid).order_by(File.version.desc()).first()


class ProcessProcessLink(SQLAlchemyBase):
    __tablename__ = 'process_join_table'
    id = Column(Integer, primary_key=True)
    child_process_uuid = Column(UUID, ForeignKey("processes.process_uuid"))
    parent_process_uuid = Column(UUID, ForeignKey("processes.process_uuid"))
    parent_process = relationship(Process, foreign_keys=[parent_process_uuid])
    child_process = relationship(Process, foreign_keys=[child_process_uuid])


class DCPQueryDBManager:
    process_file_link_ignore_duplicate_rule_sql = """
        CREATE OR REPLACE RULE process_file_join_table_ignore_duplicate_inserts AS
            ON INSERT TO process_file_join_table
                WHERE EXISTS (
                  SELECT 1
                FROM process_file_join_table
                WHERE process_uuid = NEW.process_uuid
                AND process_file_connection_type=NEW.process_file_connection_type
                AND file_uuid=NEW.file_uuid
            )
            DO INSTEAD NOTHING;
    """

    file_ignore_duplicate_rule_sql = """
        CREATE OR REPLACE RULE file_table_ignore_duplicate_inserts AS
            ON INSERT TO files
                WHERE EXISTS (
                  SELECT 1
                FROM files
                WHERE fqid = NEW.fqid
            )
            DO INSTEAD NOTHING;
    """

    bundle_ignore_duplicate_rule_sql = """
        CREATE OR REPLACE RULE bundle_table_ignore_duplicate_inserts AS
            ON INSERT TO bundles
                WHERE EXISTS (
                  SELECT 1
                FROM bundles
                WHERE fqid = NEW.fqid
            )
            DO INSTEAD NOTHING;
    """

    bundle_file_link_ignore_duplicate_rule_sql = """
        CREATE OR REPLACE RULE bundle_file_join_table_ignore_duplicate_inserts AS
            ON INSERT TO bundle_file_links
                WHERE EXISTS (
                  SELECT 1
                FROM bundle_file_links
                WHERE bundle_fqid = NEW.bundle_fqid
                AND file_fqid = NEW.file_fqid
            )
            DO INSTEAD NOTHING;
    """

    process_ignore_duplicate_rule_sql = """
        CREATE OR REPLACE RULE process_table_ignore_duplicate_inserts AS
            ON INSERT TO processes
                WHERE EXISTS (
                  SELECT 1
                FROM processes
                WHERE process_uuid = NEW.process_uuid
            )
            DO INSTEAD NOTHING;
    """

    get_all_children_function_sql = """
        CREATE or REPLACE FUNCTION get_all_children(IN parent_process_uuid UUID)
            RETURNS TABLE(child_process UUID) as $$
              WITH RECURSIVE recursive_table AS (
                SELECT child_process_uuid FROM process_join_table
                WHERE parent_process_uuid=$1
                UNION
                SELECT process_join_table.child_process_uuid FROM process_join_table
                INNER JOIN recursive_table
                ON process_join_table.parent_process_uuid = recursive_table.child_process_uuid)
            SELECT * from recursive_table;
            $$ LANGUAGE SQL;
    """

    get_all_parents_function_sql = """
        CREATE or REPLACE FUNCTION get_all_parents(IN child_process_uuid UUID)
            RETURNS TABLE(parent_process UUID) as $$
              WITH RECURSIVE recursive_table AS (
                SELECT parent_process_uuid FROM process_join_table
                WHERE child_process_uuid=$1
                UNION
                SELECT process_join_table.parent_process_uuid FROM process_join_table
                INNER JOIN recursive_table
                ON process_join_table.child_process_uuid = recursive_table.parent_process_uuid)
            SELECT * from recursive_table;
            $$ LANGUAGE SQL;
    """

    def init_db(self, dry_run=True):
        from sqlalchemy_utils import database_exists, create_database

        logger.info("Initializing database at %s", repr(config.db.url))
        if not database_exists(config.db.url):
            logger.info("Creating database")
            create_database(config.db.url)
        logger.info("Initializing database")

        if dry_run:
            orig_db_engine_params = dict(config._db_engine_params)
            config._db_engine_params.update(strategy="mock", executor=lambda sql, *args, **kwargs: print(sql))

        SQLAlchemyBase.metadata.create_all(config.db)
        self.create_recursive_functions_in_db()
        self.create_upsert_rules_in_db()

        if dry_run:
            config._db_engine_params = orig_db_engine_params

    def create_upsert_rules_in_db(self):
        config.db_session.execute(
            self.bundle_file_link_ignore_duplicate_rule_sql + self.bundle_ignore_duplicate_rule_sql
        )
        config.db_session.execute(
            self.process_file_link_ignore_duplicate_rule_sql + self.process_ignore_duplicate_rule_sql
        )
        config.db_session.execute(self.file_ignore_duplicate_rule_sql)
        config.db_session.commit()

    def create_recursive_functions_in_db(self):
        config.db_session.execute(self.get_all_children_function_sql + self.get_all_parents_function_sql)
        config.db_session.commit()

    def drop_db(self, dry_run=True):
        from sqlalchemy_utils import database_exists, drop_database
        if database_exists(config.db.url):
            if dry_run:
                logger.critical("Would drop database %s", config.db.url)
            else:
                drop_database(config.db.url)


def run_query(query, rows_per_page=100):
    try:
        cursor = config.db_session.execute(query)
        while True:
            rows = cursor.fetchmany(size=rows_per_page)
            for row in rows:
                yield row
            if not rows:
                break

    except sqlalchemy_exceptions.ProgrammingError as e:
        raise DCPQueryError(title=e.orig.pgerror, detail={"pgcode": e.orig.pgcode})
    except sqlalchemy_exceptions.OperationalError as e:
        if "canceling statement due to statement timeout" in str(e):
            raise QueryTimeoutError(title=e.orig.pgerror, detail={"pgcode": e.orig.pgcode})
        else:
            raise
