from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from dcpquery.db.models import SQLAlchemyBase
from dcpquery.db.models.admin import User
from dcpquery.db.models.base import DCPModelMixin
from dcpquery.db.models.biomaterial import Biomaterial, CellLine, CellSuspension, DonorOrganism, Specimen
from dcpquery.db.models.data_file import DCPFile, SequenceFile
from dcpquery.db.models.modules import Accession, Publication, Ontology


class UserAccessGroupJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "user_access_group_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    user_uuid = Column(UUID, ForeignKey('users.uuid'), primary_key=True)
    access_group_uuid = Column(UUID, ForeignKey('access_groups.uuid'), primary_key=True)
    user = relationship(User)
    access_group = relationship("AccessGroup")


class BiomaterialAccessionJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "biomaterial_accession_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    accession_uuid = Column(UUID, ForeignKey('accessions.uuid'), primary_key=True)
    biomaterial_uuid = Column(UUID, ForeignKey('biomaterials.uuid'), primary_key=True)
    accession = relationship(Accession)
    biomaterial = relationship(Biomaterial)


class CellLinePublicationJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "cell_line_publication_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    cell_line_uuid = Column(UUID, ForeignKey('cell_lines.uuid'), primary_key=True)
    publication_uuid = Column(UUID, ForeignKey('publications.uuid'), primary_key=True)
    cell_line = relationship(CellLine)
    publication = relationship(Publication)


class CellSuspensionCellTypeOntologyJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "cell_suspension_cell_type_ontology_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    cell_suspension_uuid = Column(UUID, ForeignKey('cell_suspensions.uuid'), primary_key=True)
    cell_type_ontology_uuid = Column(UUID, ForeignKey('ontologies.uuid'), primary_key=True)
    cell_suspension = relationship(CellSuspension, foreign_keys=[cell_suspension_uuid])
    cell_type_ontology = relationship(Ontology, foreign_keys=[cell_type_ontology_uuid])


class DonorOrganismDiseaseOntologyJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "donor_organism_disease_ontology_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    donor_organism_uuid = Column(UUID, ForeignKey('donor_organism.uuid'), primary_key=True)
    disease_ontology_uuid = Column(UUID, ForeignKey('ontologies.uuid'), primary_key=True)
    donor_organism = relationship(DonorOrganism, foreign_keys=[donor_organism_uuid])
    disease_ontology = relationship(Ontology, foreign_keys=[disease_ontology_uuid])


class SpecimenDiseaseOntologyJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "specimen_disease_ontology_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    specimen_uuid = Column(UUID, ForeignKey('specimens.uuid'), primary_key=True)
    disease_ontology_uuid = Column(UUID, ForeignKey('ontologies.uuid'), primary_key=True)
    specimen = relationship(Specimen, foreign_keys=[specimen_uuid])
    disease_ontology = relationship(Ontology, foreign_keys=[disease_ontology_uuid])


class FileOntologyJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "file_ontology_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    file_uuid = Column(UUID, ForeignKey('files.uuid'), primary_key=True)
    ontology_uuid = Column(UUID, ForeignKey('ontologies.uuid'), primary_key=True)
    file = relationship(DCPFile, foreign_keys=[file_uuid])
    ontology = relationship(Ontology, foreign_keys=[ontology_uuid])


class SequenceFileAccessionJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "sequence_file_accession_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    sequence_file_uuid = Column(UUID, ForeignKey('sequence_files.uuid'), primary_key=True)
    accession_uuid = Column(UUID, ForeignKey('accessions.uuid'), primary_key=True)
    accession = relationship(Accession, foreign_keys=[accession_uuid])
    sequence_file = relationship(SequenceFile, foreign_keys=[sequence_file_uuid])