import enum

from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship

from dcpquery.db.models.base import DCPModelMixin
from dcpquery.db.models import SQLAlchemyBase


class User(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "users"

    phone_number = Column(String)
    name = Column(String)
    email = Column(String)
    address = Column(String)
    country = Column(String)
    orcid_id = Column(String)
    access_groups = relationship("AccessGroup", secondary="user_access_group_join_table")


class UserAccessGroupJoinTable(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "user_access_group_join_table"
    user = relationship(User)
    access_group = relationship("AccessGroup")


class PermissionTypeEnum(enum.Enum):
    READ = "READ"
    WRITE = "WRITE"
    DELETE = "DELETE"


class AccessGroup(DCPModelMixin, SQLAlchemyBase):
    __tablename__ = "access_groups"
    permission = Column(Enum(PermissionTypeEnum))
