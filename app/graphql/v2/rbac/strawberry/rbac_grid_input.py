import strawberry
from commons.db.v6 import (
    RbacPrivilegeOptionEnum,
    RbacPrivilegeTypeEnum,
    RbacResourceEnum,
    RbacRoleEnum,
)


@strawberry.input
class RbacGridRolePrivilegeInput:
    privilege: RbacPrivilegeTypeEnum
    option: RbacPrivilegeOptionEnum


@strawberry.input
class RbacGridRoleInput:
    role: RbacRoleEnum
    privileges: list[RbacGridRolePrivilegeInput]


@strawberry.input
class RbacGridInput:
    resource: RbacResourceEnum
    roles: list[RbacGridRoleInput]


@strawberry.input
class UpdateCommissionVisibilityInput:
    role: RbacRoleEnum
    commission: bool
