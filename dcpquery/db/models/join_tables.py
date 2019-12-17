from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from dcpquery.db.models import SQLAlchemyBase
from dcpquery.db.models.admin import User
from dcpquery.db.models.base import DCPModelMixin


class UserAccessGroupJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "user_access_group_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    user_uuid = Column(UUID(as_uuid=True), ForeignKey('users.uuid'), primary_key=True)
    access_group_uuid = Column(UUID(as_uuid=True), ForeignKey('access_groups.uuid'), primary_key=True)
    user = relationship("User")
    access_group = relationship("AccessGroup")


class BiomaterialAccessionJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "biomaterial_accession_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    accession_id = Column(String, ForeignKey('accessions.id'), primary_key=True)
    biomaterial_uuid = Column(UUID(as_uuid=True), ForeignKey('biomaterials.uuid'), primary_key=True)
    accession = relationship("Accession", foreign_keys=[accession_id])
    biomaterial = relationship("Biomaterial",  foreign_keys=[biomaterial_uuid])


class CellLinePublicationJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "cell_line_publication_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    cell_line_uuid = Column(UUID(as_uuid=True), ForeignKey('cell_lines.uuid'), primary_key=True)
    publication_uuid = Column(UUID(as_uuid=True), ForeignKey('publications.uuid'), primary_key=True)
    cell_line = relationship("CellLine")
    publication = relationship("Publication")


class CellSuspensionCellTypeOntologyJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "cell_suspension_cell_type_ontology_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    cell_suspension_uuid = Column(UUID(as_uuid=True), ForeignKey('cell_suspensions.uuid'), primary_key=True)
    cell_type_ontology_id = Column(String, ForeignKey('ontologies.ontology'), primary_key=True)
    cell_suspension = relationship("CellSuspension", foreign_keys=[cell_suspension_uuid])
    cell_type_ontology = relationship("Ontology", foreign_keys=[cell_type_ontology_id])


class DonorOrganismDiseaseOntologyJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "donor_organism_disease_ontology_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    donor_organism_uuid = Column(UUID(as_uuid=True), ForeignKey('donor_organism.uuid'), primary_key=True)
    disease_ontology_id = Column(String, ForeignKey('ontologies.ontology'), primary_key=True)
    donor_organism = relationship("DonorOrganism", foreign_keys=[donor_organism_uuid])
    disease_ontology = relationship("Ontology", foreign_keys=[disease_ontology_id])


class SpecimenDiseaseOntologyJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "specimen_disease_ontology_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    specimen_uuid = Column(UUID(as_uuid=True), ForeignKey('specimens.uuid'), primary_key=True)
    disease_ontology_id = Column(String, ForeignKey('ontologies.ontology'), primary_key=True)
    specimen = relationship("Specimen", foreign_keys=[specimen_uuid])
    disease_ontology = relationship("Ontology", foreign_keys=[disease_ontology_id])


class FileOntologyJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "file_ontology_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    file_uuid = Column(UUID(as_uuid=True), ForeignKey('files.uuid'), primary_key=True)
    ontology_id = Column(String, ForeignKey('ontologies.ontology'), primary_key=True)
    file = relationship("DCPFile", foreign_keys=[file_uuid])
    ontology = relationship("Ontology", foreign_keys=[ontology_id])


class SequenceFileAccessionJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "sequence_file_accession_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    sequence_file_uuid = Column(UUID(as_uuid=True), ForeignKey('sequence_files.uuid'), primary_key=True)
    accession_id = Column(String, ForeignKey('accessions.id'), primary_key=True)
    accession = relationship("Accession", foreign_keys=[accession_id])
    sequence_file = relationship("SequenceFile", foreign_keys=[sequence_file_uuid])


class ProjectContributorJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "project_contributor_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    project_uuid = Column(UUID(as_uuid=True), ForeignKey('projects.uuid'), primary_key=True)
    contributor_uuid = Column(UUID(as_uuid=True), ForeignKey('contributors.uuid'), primary_key=True)
    project = relationship("Project", foreign_keys=[project_uuid])
    contributor = relationship("Contributor", foreign_keys=[contributor_uuid])


class ProjectPublicationJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "project_publication_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    project_uuid = Column(UUID(as_uuid=True), ForeignKey('projects.uuid'), primary_key=True)
    publication_uuid = Column(UUID(as_uuid=True), ForeignKey('publications.uuid'), primary_key=True)
    publication = relationship("Publication", foreign_keys=[publication_uuid])
    project = relationship("Project", foreign_keys=[project_uuid])


class ProjectURLJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "project_url_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    project_uuid = Column(UUID(as_uuid=True), ForeignKey('projects.uuid'), primary_key=True)
    url_name = Column(String, ForeignKey('urls.url'), primary_key=True)
    project = relationship("Project", foreign_keys=[project_uuid])
    url = relationship("URL_Object", foreign_keys=[url_name])


class ProjectFunderJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "project_funder_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    project_uuid = Column(UUID(as_uuid=True), ForeignKey('projects.uuid'), primary_key=True)
    funder_uuid = Column(UUID(as_uuid=True), ForeignKey('funders.uuid'), primary_key=True)
    project = relationship("Project", foreign_keys=[project_uuid])
    funder = relationship("Funder", foreign_keys=[funder_uuid])


class ProjectAccessionJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "project_accession_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    project_uuid = Column(UUID(as_uuid=True), ForeignKey('projects.uuid'), primary_key=True)
    accession_id = Column(String, ForeignKey('accessions.id'), primary_key=True)
    project = relationship("Project", foreign_keys=[project_uuid])
    accession = relationship("Accession", foreign_keys=[accession_id])


class ProjectAccessGroupJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "project_access_group_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    project_uuid = Column(UUID(as_uuid=True), ForeignKey('projects.uuid'), primary_key=True)
    access_group_uuid = Column(UUID(as_uuid=True), ForeignKey('access_groups.uuid'), primary_key=True)
    access_group = relationship("AccessGroup", foreign_keys=[access_group_uuid])
    project = relationship("Project", foreign_keys=[project_uuid])


class ProtocolReagentJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "protocol_reagent_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    protocol_uuid = Column(UUID(as_uuid=True), ForeignKey('protocols.uuid'), primary_key=True)
    reagent_uuid = Column(UUID(as_uuid=True), ForeignKey('reagents.uuid'), primary_key=True)
    protocol = relationship("Protocol", foreign_keys=[protocol_uuid])
    reagent = relationship("PurchasedReagent", foreign_keys=[reagent_uuid])


class ProcessParameterJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "process_parameter_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    process_uuid = Column(UUID(as_uuid=True), ForeignKey('processes.uuid'), primary_key=True)
    parameter_uuid = Column(UUID(as_uuid=True), ForeignKey('parameters.uuid'), primary_key=True)
    process = relationship("Process", foreign_keys=[process_uuid])
    parameter = relationship("Parameter", foreign_keys=[parameter_uuid])


class ProcessTaskJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "process_task_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    process_uuid = Column(UUID(as_uuid=True), ForeignKey('processes.uuid'), primary_key=True)
    task_uuid = Column(UUID(as_uuid=True), ForeignKey('tasks.uuid'), primary_key=True)
    process = relationship("Process", foreign_keys=[process_uuid])
    task = relationship("Task", foreign_keys=[task_uuid])