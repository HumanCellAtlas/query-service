import datetime
import logging

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship


logger = logging.getLogger(__name__)


class DCPModelMixin(object):
    __tablename__ = 'dcp_base'
    uuid = Column(UUID, nullable=False, index=True, primary_key=True)
    """"
    PROBLEM?
    Because the versioning feature relies upon comparison of the in memory record of an object, the feature only applies
     to the Session.flush() process, where the ORM flushes individual in-memory rows to the database. It does not 
     take effect when performing a multirow UPDATE or DELETE using Query.update() or Query.delete() methods, 
     as these methods only emit an UPDATE or DELETE statement but otherwise do not have direct access to the 
     contents of those rows being affected.


    """

    version_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    @declared_attr
    def created_by(cls):
        return relationship("User")

    @declared_attr
    def updated_by(cls):
        return relationship("User")
    # access_control_groups = Column("AccessGroup) start just on project level

    __mapper_args__ = {
        "version_id_col": version_id
    }


    # def create(self):
    #     pass
    #
    # def update(self):
    #     pass
    #
    # def delete(self):
    #     pass
    #
    # def delete_many(self):
    #     pass
    #
    # def select_one(self):
    #     pass
    #
    # def filter(self):
    #     pass


