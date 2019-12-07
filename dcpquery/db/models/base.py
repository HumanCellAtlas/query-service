import datetime
import logging

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from dcpquery import config

logger = logging.getLogger(__name__)


db = config.db_session


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
    _repr_hide = ['created_at', 'updated_at', 'created_by', 'updated_by']

    @classmethod
    def query(cls):
        return db.query(cls)

    @classmethod
    def get(cls, uuid):
        return cls.query.get(uuid)

    @classmethod
    def get_by(cls, **kw):
        return cls.query.filter_by(**kw).first()

    @classmethod
    def get_or_create(cls, **kw):
        r = cls.get_by(**kw)
        if not r:
            r = cls(**kw)
            db.add(r)

        return r

    @classmethod
    def create(cls, **kw):
        r = cls(**kw)
        db.add(r)
        return r

    def save(self):
        db.add(self)

    def delete(self):
        db.delete(self)

    def __repr__(self):
        values = ', '.join("%s=%r" % (n, getattr(self, n)) for n in self.__table__.c.keys() if n not in self._repr_hide)
        return "%s(%s)" % (self.__class__.__name__, values)

    def filter_string(self):
        return self.__str__()
