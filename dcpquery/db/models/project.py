from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from dcpquery.db.models import SQLAlchemyBase
from dcpquery.db.models.base import DCPModelMixin


class Project(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "projects"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
    processes = relationship("Process", secondary="process_project_join_table")


class ProjectContributorJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "project_contributor_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    project_uuid = Column(UUID, ForeignKey('projects.uuid'), primary_key=True)
    contributor_uuid = Column(UUID, ForeignKey('contributors.uuid'), primary_key=True)
    project = relationship(Project, foreign_keys=[project_uuid])
    contributor = relationship("Contributor", foreign_keys=[contributor_uuid])


class ProjectPublicationJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "project_publication_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    project_uuid = Column(UUID, ForeignKey('projects.uuid'), primary_key=True)
    publication_uuid = Column(UUID, ForeignKey('publications.uuid'), primary_key=True)
    publication = relationship("Publication", foreign_keys=[publication_uuid])
    project = relationship(Project, foreign_keys=[project_uuid])


class ProjectFunderJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "project_funder_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    project_uuid = Column(UUID, ForeignKey('projects.uuid'), primary_key=True)
    funder_uuid = Column(UUID, ForeignKey('funders.uuid'), primary_key=True)
    project = relationship(Project, foreign_keys=[project_uuid])
    funder = relationship("Funder", foreign_keys=[funder_uuid])


class ProjectLinkJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "project_link_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    project_uuid = Column(UUID, ForeignKey('projects.uuid'), primary_key=True)
    link_uuid = Column(UUID, ForeignKey('links.uuid'), primary_key=True)
    project = relationship(Project, foreign_keys=[project_uuid])
    link = relationship("Link", foreign_keys=[link_uuid])


class ProjectAccessionJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "project_accession_join_table"

    def __init__(self, project, accession, *args, **kwargs):
        super().__init__(*args, **kwargs)

    project_uuid = Column(UUID, ForeignKey('projects.uuid'), primary_key=True)
    accessions_uuid = Column(UUID, ForeignKey('accessions.uuid'), primary_key=True)
    project = relationship(Project, foreign_keys=[project_uuid])
    accession = relationship("Accession", foreign_keys=[accessions_uuid])


class ProjectAccessGroupJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "project_access_group_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    project_uuid = Column(UUID, ForeignKey('projects.uuid'), primary_key=True)
    access_group_uuid = Column(UUID, ForeignKey('access_groups.uuid'), primary_key=True)
    access_group = relationship("AccessGroup", foreign_keys=[access_group_uuid])
    project = relationship(Project, foreign_keys=[project_uuid])
