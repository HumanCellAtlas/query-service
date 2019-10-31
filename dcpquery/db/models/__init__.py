import enum
import logging
import typing
from typing import List

from sqlalchemy import Column, String, DateTime, ForeignKey, BigInteger, UniqueConstraint, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from dcpquery import config

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
    __tablename__ = 'bundles_all_versions'
    fqid = Column(String, primary_key=True, unique=True, nullable=False, index=True)
    uuid = Column(UUID, nullable=False, index=True)
    version = Column(DateTime, nullable=False, index=True)
    manifest = Column(MutableDict.as_mutable(JSONB))
    aggregate_metadata = Column(MutableDict.as_mutable(JSONB))
    files = relationship("File", secondary='bundle_file_links')

    @classmethod
    def delete_bundles(cls, bundle_fqids):
        config.db_session.execute("""
                                DELETE FROM bundles_all_versions WHERE fqid IN :bundle_fqid_list;
                                """, {"bundle_fqid_list": tuple(bundle_fqids)})
        config.db_session.commit()

    @classmethod
    def select_bundle(cls, bundle_fqid):
        return config.db_session.query(cls).filter(cls.fqid == bundle_fqid).one_or_none()


class DCPMetadataSchemaType(SQLAlchemyBase):
    __tablename__ = 'dcp_metadata_schema_types'
    name = Column(String, primary_key=True, nullable=False)
    files = relationship("File", back_populates='dcp_schema_type')


class Project(DCPQueryModelHelper, SQLAlchemyBase):
    __tablename__ = 'projects_all_versions'
    fqid = Column(String, primary_key=True, index=True)
    uuid = Column(UUID, nullable=False, index=True)
    version = Column(DateTime, nullable=False, index=True)
    files = relationship("File", secondary="project_file_join_table")

    @classmethod
    def delete_many(cls, project_fqids):
        if len(project_fqids) > 0:
            config.db_session.execute(
                "DELETE FROM projects_all_versions WHERE fqid IN :project_fqid_list;",
                {"project_fqid_list": tuple(project_fqids)})
            config.db_session.commit()

    @classmethod
    def select_one(cls, project_fqid):
        return config.db_session.query(cls).filter(cls.fqid == project_fqid).one_or_none()


class File(DCPQueryModelHelper, SQLAlchemyBase):
    __tablename__ = 'files_all_versions'
    fqid = Column(String, primary_key=True, unique=True, nullable=False, index=True)
    uuid = Column(UUID, nullable=False, index=True)
    version = Column(DateTime, nullable=False, index=True)
    dcp_schema_type_name = Column(String, ForeignKey("dcp_metadata_schema_types.name"))
    dcp_schema_type = relationship("DCPMetadataSchemaType", back_populates="files")
    body = Column(MutableDict.as_mutable(JSONB))
    content_type = Column(String)
    size = Column(BigInteger)
    extension = Column(String)
    schema_major_version = Column(Integer, index=True)
    schema_minor_version = Column(Integer, index=True)
    bundles = relationship("Bundle", secondary='bundle_file_links')
    projects = relationship("Project", secondary="project_file_join_table")

    @classmethod
    def select_file(cls, file_fqid):
        return config.db_session.query(cls).filter(cls.fqid == file_fqid).one_or_none()

    @classmethod
    def delete_files(cls, file_fqids):
        if len(file_fqids) > 0:
            ProjectFileLink.delete_links_for_files(file_fqids)
            config.db_session.execute(
                "DELETE FROM files_all_versions WHERE fqid IN :file_fqid_list;",
                {"file_fqid_list": tuple(file_fqids)})
            config.db_session.commit()


class ProjectFileLink(SQLAlchemyBase):
    __tablename__ = 'project_file_join_table'
    project_fqid = Column(String, ForeignKey('projects_all_versions.fqid'), primary_key=True, index=True)
    file_fqid = Column(String, ForeignKey('files_all_versions.fqid'), primary_key=True, index=True)
    project = relationship(Project)
    file = relationship(File)
    __table_args__ = (UniqueConstraint(
        'project_fqid', 'file_fqid', name='project_file_uc'),)

    @classmethod
    def select_links_for_file_fqids(cls, file_fqids: List[str]):
        links = cls.__table__.select().where(cls.file_fqid.in_(file_fqids))
        return config.db_session.execute(links)

    @classmethod
    def delete_links_for_files(cls, file_fqids: List[str]):
        if len(file_fqids) > 0:
            config.db_session.execute("""
            DELETE FROM project_file_join_table WHERE file_fqid IN :file_fqid_list;
            """, {"file_fqid_list": tuple(file_fqids)})
            config.db_session.commit()

    @classmethod
    def select_links_for_project_fqids(cls, project_fqids: List[str]):
        if len(project_fqids) > 0:
            return config.db_session.execute("""
                  SELECT project_fqid, file_fqid FROM project_file_join_table WHERE project_fqid IN :project_fqid_list;
                    """, {"project_fqid_list": tuple(project_fqids)}).fetchall()
        return []


class BundleFileLink(SQLAlchemyBase):
    __tablename__ = 'bundle_file_links'
    bundle_fqid = Column(String, ForeignKey('bundles_all_versions.fqid'), primary_key=True, index=True)
    file_fqid = Column(String, ForeignKey('files_all_versions.fqid'), primary_key=True, index=True)
    bundle = relationship(Bundle)
    file = relationship(File)
    name = Column(String, nullable=False)

    @classmethod
    def delete_links_for_bundles(cls, bundle_fqids: List[str]):
        if len(bundle_fqids) > 0:
            config.db_session.execute("""
                    DELETE FROM bundle_file_links WHERE bundle_fqid IN :bundle_fqid_list;
                    """, {"bundle_fqid_list": tuple(bundle_fqids)})
            config.db_session.commit()

    @classmethod
    def delete_links_for_files(cls, file_fqids: List[str]):
        if len(file_fqids) > 0:
            config.db_session.execute("""
                            DELETE FROM bundle_file_links WHERE file_fqid IN :file_fqid_list;
                            """, {"file_fqid_list": tuple(file_fqids)})
            config.db_session.commit()

    @classmethod
    def select_links_for_bundle_fqids(cls, bundle_fqids: List[str]):
        links = cls.__table__.select().where(cls.bundle_fqid.in_(bundle_fqids))
        return config.db_session.execute(links)

    @classmethod
    def select_links_for_file_fqids(cls, file_fqids: List[str]):
        links = cls.__table__.select().where(cls.file_fqid.in_(file_fqids))
        return config.db_session.execute(links)


class ConnectionTypeEnum(enum.Enum):
    INPUT_ENTITY = 'INPUT_ENTITY'
    OUTPUT_ENTITY = 'OUTPUT_ENTITY'
    PROTOCOL_ENTITY = 'PROTOCOL_ENTITY'


class Process(SQLAlchemyBase):
    __tablename__ = 'processes_for_graph'
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
    process_uuid = Column(UUID, ForeignKey("processes_for_graph.process_uuid"), index=True)
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
    child_process_uuid = Column(UUID, ForeignKey("processes_for_graph.process_uuid"), index=True)
    parent_process_uuid = Column(UUID, ForeignKey("processes_for_graph.process_uuid"), index=True)
    parent_process = relationship(Process, foreign_keys=[parent_process_uuid])
    child_process = relationship(Process, foreign_keys=[child_process_uuid])
    __table_args__ = (UniqueConstraint('child_process_uuid', 'parent_process_uuid', name='unq_process_combo'),)
