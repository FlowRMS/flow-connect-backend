from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import UserBaseModel
from app.graphql.v2.rbac.models.enums.rbac_privilege_option_enum import RbacPrivilegeOptionEnum
from app.graphql.v2.rbac.models.enums.rbac_privilege_type_enum import RbacPrivilegeTypeEnum
from app.graphql.v2.rbac.models.enums.rbac_resource_enum import RbacResourceEnum
from app.graphql.v2.rbac.models.enums.rbac_role_enum import RbacRoleEnum


class RbacPermission(UserBaseModel):
    __tablename__ = "rbac_permissions"

    role: Mapped[RbacRoleEnum] = mapped_column(Integer, default=None)
    resource: Mapped[RbacResourceEnum] = mapped_column(Integer, default=None)
    privilege: Mapped[RbacPrivilegeTypeEnum] = mapped_column(Integer, default=None)
    option: Mapped[RbacPrivilegeOptionEnum] = mapped_column(Integer, default=None)
