from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from dcpquery.db.join_tables.process import Process
from dcpquery.db.models import SQLAlchemyBase
from dcpquery.db.models.base import DCPModelMixin
from dcpquery.db.models.modules import Parameter, Task


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