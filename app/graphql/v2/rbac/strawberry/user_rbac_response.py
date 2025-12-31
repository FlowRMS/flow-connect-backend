import strawberry
from commons.db.v6 import RbacPrivilegeOptionEnum, RbacPrivilegeTypeEnum


@strawberry.type
class Privilege:
    privilege: RbacPrivilegeTypeEnum
    option: RbacPrivilegeOptionEnum


@strawberry.type
class UserRbac:
    privileges: list[Privilege]
    commission: bool
