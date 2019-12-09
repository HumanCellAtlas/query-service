import datetime
import logging

from uuid import uuid4
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from dcpquery import config

logger = logging.getLogger(__name__)

db = config.db_session


class MissingUUIDException(Exception):
    pass


class DCPModelMixin(object):
    __tablename__ = 'dcp_base'
    # provenance.document_id
    uuid = Column(UUID(as_uuid=True), nullable=False, index=True, primary_key=True, default=uuid4())
    """"
    PROBLEM?
    Because the versioning feature relies upon comparison of the in memory record of an object, the feature only applies
     to the Session.flush() process, where the ORM flushes individual in-memory rows to the database. It does not 
     take effect when performing a multirow UPDATE or DELETE using Query.update() or Query.delete() methods, 
     as these methods only emit an UPDATE or DELETE statement but otherwise do not have direct access to the 
     contents of those rows being affected.


 SAWarning: Inheriting version_id_col 'None' does not match inherited version_id_col 'version_id' and will not 
 automatically populate the inherited versioning column. version_id_col should only be specified on the base-most 
 mapper that includes versioning.


Columns generated by declared_attr can also be referenced by __mapper_args__ to a limited degree, 
currently by polymorphic_on and version_id_col; the declarative extension will resolve them at class construction time:



    """

    version_id = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    # TODO current bug -> Trying to redefine primary-key column 'uuid' as a non-primary-key column on table 'users'
    # @declared_attr
    # def created_by_uuid(cls):
    #     return Column('uuid', ForeignKey('user.uuid'))
    #
    # @declared_attr
    # def updated_by_uuid(cls):
    #     return Column('uuid', ForeignKey('user.uuid'))
    #
    # @declared_attr
    # def created_by(cls):
    #     return relationship("User")
    #
    # @declared_attr
    # def updated_by(cls):
    #     return relationship("User")

    # access_control_groups = Column("AccessGroup) start just on project level

    __mapper_args__ = {
        "version_id_col": version_id
    }
    _repr_hide = ['created_at', 'updated_at']

    @classmethod
    def query(cls):
        return db.query(cls)

    @classmethod
    def get(cls, uuid):
        return config.db_session.query(cls).filter(cls.uuid == uuid).one_or_none()

    #
    # @classmethod
    # def get_by(cls, **kw):
    #     return cls.query.filter_by(**kw).first()
    #
    # @classmethod
    # def get_or_create(cls, **kw):
    #     r = cls.get_by(**kw)
    #     if not r:
    #         r = cls(**kw)
    #         db.add(r)
    #
    #     return r
    #
    @classmethod
    def create(cls, uuid=None, **kw):
        if not uuid:
            if cls in ('biomaterials', 'protocols', 'projects', 'files', 'processes'):
                raise MissingUUIDException
            else:
                uuid = str(uuid4())
        r = cls(uuid=uuid, **kw)
        config.db_session.add(r)
        config.db_session.commit()
        return r

    @classmethod
    def get_or_create(cls, uuid, **kw):
        existing_object = cls.get(uuid)
        if existing_object:
            return existing_object
        try:
            return cls.create(uuid=uuid, **kw)
        except Exception as e:
            import pdb
            pdb.set_trace()
            logger.info(f"SOMETHING WENT WRONG: CLS: {cls}, uuid: {uuid}, exception: {e} ")
            config.db_session.rollback()

    #
    # def save(self):
    #     db.add(self)
    #
    # def delete(self):
    #     db.delete(self)
    #
    # def __repr__(self):
    #     values = ', '.join("%s=%r" % (n, getattr(self, n)) for n in self.__table__.c.keys() if n not in self._repr_hide)
    #     return "%s(%s)" % (self.__class__.__name__, values)
    #
    # def filter_string(self):
    #     return self.__str__()
