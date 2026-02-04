import strawberry
from commons.db.v6 import (
    RbacPrivilegeOptionEnum,
    RbacPrivilegeTypeEnum,
)


@strawberry.input
class RbacGridRolePrivilegeInput:
    privilege: RbacPrivilegeTypeEnum
    option: RbacPrivilegeOptionEnum
