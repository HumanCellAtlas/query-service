import enum

from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from dcpquery.db.models import SQLAlchemyBase
from dcpquery.db.models.base import DCPModelMixin

from dcpquery.db.models.biomaterial import Biomaterial
from dcpquery.db.models.cell import Cell
from dcpquery.db.models.modules import Ontology, Accession, Task, Parameter
from dcpquery.db.models.project import Project
from dcpquery.db.models.protocol import Protocol


class RunTypeEnum(enum.Enum):
    pass


class Process(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "process"
    body = Column(MutableDict.as_mutable(JSONB))
    name = Column(String)
    description = Column(String)
    location = Column(String)
    # todo figure out what operators are
    # operators = relationship("Operators")  # ????
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    type = relationship(Ontology)
    deviation_from_protocol = Column(String)
    accession = relationship(Accession)
    tasks = relationship("Task", secondary="process_task_join_table")
    input_bundle = Column(String)  # use for etl then drop column
    inputs = relationship("Parameter", secondary="process_parameter_join_table")
    analysis_run_type = Column(Enum(RunTypeEnum))


class ProcessParameterJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "process_parameter_join_table"
    process = relationship(Process)
    parameter = relationship(Parameter)


class ProcessTaskJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "process_task_join_table"
    process = relationship(Process)
    task = relationship(Task)


class ProcessJoinTable(DCPModelMixin, SQLAlchemyBase):
    parent_process = relationship(Process)
    child_process = relationship(Process)


class ProcessConnectionTypeEnum(enum.Enum):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    PROTOCOL = "PROTOCOL"


class ProcessFileJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "process_file_join_table"
    process = relationship(Process)
    file = relationship("File")
    connection_type = Column(Enum(ProcessConnectionTypeEnum))
    project = relationship(Project)


class ProcessBiomaterialJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "process_biomaterial_join_table"
    process = relationship(Process)
    biomaterial = relationship(Biomaterial)
    connection_type = Column(Enum(ProcessConnectionTypeEnum))
    project = relationship(Project)


class ProcessProtocolJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "process_protocol_join_table"
    process = relationship(Process)
    protocol = relationship(Protocol)
    connection_type = Column(Enum(ProcessConnectionTypeEnum), default=ProcessConnectionTypeEnum.PROTOCOL)
    project = relationship(Project)


class ProcessCellJoinTable(DCPModelMixin, SQLAlchemyBase):  # will need to update process process join table generation
    __tablename__ = "process_cell_join_table"
    process = relationship(Process)
    cell = relationship(Cell)
    connection_type = Column(Enum(ProcessConnectionTypeEnum))
    project = relationship(Project)
