import strawberry
from commons.db.v6 import (
    RbacPrivilegeOptionEnum,
    RbacPrivilegeTypeEnum,
    RbacResourceEnum,
    RbacRoleEnum,
)


@strawberry.type
class RbacPrivilegeResponse:
    privilege: RbacPrivilegeTypeEnum
    option: RbacPrivilegeOptionEnum


@strawberry.type
class RbacRolePermissionResponse:
    role_name: RbacRoleEnum
    privileges: list[RbacPrivilegeResponse]


@strawberry.type
class RbacGridResponse:
    resource: RbacResourceEnum
    roles: list[RbacRolePermissionResponse]
