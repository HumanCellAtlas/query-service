from sqlalchemy import Column, String, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from dcpquery.db.models.base import DCPModelMixin
from dcpquery.db.models import SQLAlchemyBase
from dcpquery.db.models.enums import PermissionTypeEnum


class User(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "users"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    phone_number = Column(String)
    name = Column(String)
    email = Column(String)
    address = Column(String)
    country = Column(String)
    orcid_id = Column(String)
    access_groups = relationship("AccessGroup", secondary="user_access_group_join_table")


class AccessGroup(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "access_groups"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    permission = Column(Enum(PermissionTypeEnum))
    users = relationship(User, secondary="user_access_group_join_table")
