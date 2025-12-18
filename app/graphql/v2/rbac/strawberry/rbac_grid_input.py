import strawberry

from app.graphql.v2.rbac.models.enums.rbac_privilege_option_enum import RbacPrivilegeOptionEnum
from app.graphql.v2.rbac.models.enums.rbac_privilege_type_enum import RbacPrivilegeTypeEnum
from app.graphql.v2.rbac.models.enums.rbac_resource_enum import RbacResourceEnum


@strawberry.input
class RbacGridRolePrivilegeInput:
    privilege: RbacPrivilegeTypeEnum
    option: RbacPrivilegeOptionEnum


@strawberry.input
class RbacGridRoleInput:
    role_name: str
    privileges: list[RbacGridRolePrivilegeInput]


@strawberry.input
class RbacGridInput:
    resource: RbacResourceEnum
    roles: list[RbacGridRoleInput]