from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from dcpquery.db.models import SQLAlchemyBase
from dcpquery.db.models.base import DCPModelMixin


class Project(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "projects"
    short_name = Column(String, index=True, nullable=False)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    contributors = relationship("Contributor", secondary="project_contributor_join_table")
    publications = relationship("Publication", secondary="project_publication_join_table")
    funders = relationship("Funder", secondary="project_funder_join_table")
    supplementary_links = relationship("Link", secondary="project_link_join_table")
    accessions = relationship("Accession", secondary="project_accession_join_table")
    access_control_groups = relationship("AccessGroup", secondary="project_access_group_join_table")
    body = Column(MutableDict.as_mutable(JSONB))


class ProjectContributorJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "project_contributor_join_table"
    project = relationship(Project)
    contributor = relationship("Contributor")


class ProjectPublicationJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "project_publication_join_table"
    project = relationship(Project)
    publication = relationship("Publication")


class ProjectFunderJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "project_funder_join_table"
    project = relationship(Project)
    funder = relationship("Funder")


class ProjectLinkJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "project_link_join_table"
    project = relationship(Project)
    link = relationship("Link")


class ProjectAccessionJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "project_accession_join_table"
    project = relationship(Project)
    accession = relationship("Accession")


class ProjectAccessGroupJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "project_access_group_join_table"
    project = relationship(Project)
    access_group = relationship("AccessGroup")
