from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import UserBaseModel
from app.graphql.v2.rbac.models.enums import RbacRoleEnum, RbacResourceEnum, RbacPrivilegeTypeEnum, \
    RbacPrivilegeOptionEnum


class RbacPermission(UserBaseModel):
    __tablename__ = "rbac_permissions"

    role: Mapped[RbacRoleEnum] = mapped_column(Enum(RbacRoleEnum), default=None)
    resource: Mapped[RbacResourceEnum] = mapped_column(Enum(RbacResourceEnum), default=None)
    privilege: Mapped[RbacPrivilegeTypeEnum] = mapped_column(Enum(RbacPrivilegeTypeEnum), default=None)
    option: Mapped[RbacPrivilegeOptionEnum] = mapped_column(Enum(RbacPrivilegeOptionEnum), default=None)
