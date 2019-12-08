from sqlalchemy import Column, String, DateTime, Enum, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from dcpquery.db.models import SQLAlchemyBase
from dcpquery.db.models.base import DCPModelMixin

from dcpquery.db.models.biomaterial import Biomaterial
from dcpquery.db.models.cell import Cell
from dcpquery.db.models.enums import RunTypeEnum, ProcessConnectionTypeEnum
from dcpquery.db.models.modules import Ontology, Accession, Task, Parameter
from dcpquery.db.models.project import Project
from dcpquery.db.models.protocol import Protocol


class Process(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "processes"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    analysis_run_type = Column(Enum(RunTypeEnum))
    body = Column(MutableDict.as_mutable(JSONB))
    input_bundle = Column(String)  # use for etl then drop column
    name = Column(String)
    description = Column(String)
    location = Column(String)
    deviation_from_protocol = Column(String)
    # todo figure out what operators are
    # operators = relationship("Operators")  # ????
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    analysis = Column(Boolean)
    accession_uuid = Column(UUID, ForeignKey('accessions.uuid'))
    accession = relationship(Accession, foreign_keys=[accession_uuid])
    type_uuid = Column(UUID, ForeignKey('ontologies.uuid'))
    type = relationship(Ontology, foreign_keys=[type_uuid])
    tasks = relationship("Task", secondary="process_task_join_table")
    inputs = relationship("Parameter", secondary="process_parameter_join_table")
    # todo https://docs.sqlalchemy.org/en/13/orm/self_referential.html
    # direct_child_processes = relationship("Process", secondary="process_self_join_table")
    # direct_parent_processes = relationship("Process", secondary="process_self_join_table")
    projects = relationship("Project", secondary="process_project_join_table")
    files = relationship("DCPFile", secondary="process_file_join_table")
    cells = relationship("Cell", secondary="process_cell_join_table")
    protocols = relationship("Protocol", secondary="process_protocol_join_table")
    biomaterials = relationship("Biomaterial", secondary="process_biomaterial_join_table")



class ProcessParameterJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "process_parameter_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    process_uuid = Column(UUID, ForeignKey('processes.uuid'), primary_key=True)
    parameter_uuid = Column(UUID, ForeignKey('parameters.uuid'), primary_key=True)
    process = relationship(Process, foreign_keys=[process_uuid])
    parameter = relationship(Parameter, foreign_keys=[parameter_uuid])


class ProcessTaskJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "process_task_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    process_uuid = Column(UUID, ForeignKey('processes.uuid'), primary_key=True)
    task_uuid = Column(UUID, ForeignKey('tasks.uuid'), primary_key=True)
    process = relationship(Process, foreign_keys=[process_uuid])
    task = relationship(Task, foreign_keys=[task_uuid])

# join table keeping here for now to check on graph
class ProcessJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "process_self_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    parent_process_uuid = Column(UUID, ForeignKey('processes.uuid'), primary_key=True)
    child_process_uuid = Column(UUID, ForeignKey('processes.uuid'), primary_key=True)
    parent_process = relationship(Process, foreign_keys=[parent_process_uuid])
    child_process = relationship(Process, foreign_keys=[child_process_uuid])


## Todo triple check these tables for the graph -- combine into 1 table?
class ProcessFileJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "process_file_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    connection_type = Column(Enum(ProcessConnectionTypeEnum))
    process_uuid = Column(UUID, ForeignKey('processes.uuid'), primary_key=True)
    file_uuid = Column(UUID, ForeignKey('files.uuid'), primary_key=True)
    process = relationship(Process)
    file = relationship("DCPFile")


class ProcessBiomaterialJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "process_biomaterial_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    connection_type = Column(Enum(ProcessConnectionTypeEnum))
    process_uuid = Column(UUID, ForeignKey('processes.uuid'), primary_key=True)
    biomaterial_uuid = Column(UUID, ForeignKey('biomaterials.uuid'), primary_key=True)
    process = relationship(Process, foreign_keys=[process_uuid])
    biomaterial = relationship(Biomaterial, foreign_keys=[biomaterial_uuid])


class ProcessProtocolJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "process_protocol_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    connection_type = Column(Enum(ProcessConnectionTypeEnum), default=ProcessConnectionTypeEnum.PROTOCOL)
    protocol_uuid = Column(UUID, ForeignKey('protocols.uuid'), primary_key=True)
    process_uuid = Column(UUID, ForeignKey('processes.uuid'), primary_key=True)
    protocol = relationship(Protocol, foreign_keys=[protocol_uuid])
    process = relationship(Process, foreign_keys=[process_uuid])


class ProcessCellJoinTable(DCPModelMixin, SQLAlchemyBase):  # will need to update process process join table generation
    __tablename__ = "process_cell_join_table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    connection_type = Column(Enum(ProcessConnectionTypeEnum))
    cell_uuid = Column(UUID, ForeignKey('cells.uuid'), primary_key=True)
    process_uuid = Column(UUID, ForeignKey('processes.uuid'), primary_key=True)
    process = relationship(Process, foreign_keys=[process_uuid])
    cell = relationship(Cell, foreign_keys=[cell_uuid])


class ProcessProjectJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = 'process_project_join_table'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    process_uuid = Column(UUID, ForeignKey('processes.uuid'), primary_key=True)
    project_uuid = Column(UUID, ForeignKey('projects.uuid'), primary_key=True)
    process = relationship(Process, foreign_keys=[process_uuid])
    project = relationship(Project, foreign_keys=[project_uuid])
