from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB
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
    supplementary_links = relationship("URL_Object", secondary="project_url_join_table")
    accessions = relationship("Accession", secondary="project_accession_join_table")
    access_control_groups = relationship("AccessGroup", secondary="project_access_group_join_table")
    body = Column(MutableDict.as_mutable(JSONB))
    processes = relationship("Process", secondary="process_project_join_table", backref='project_processes')


