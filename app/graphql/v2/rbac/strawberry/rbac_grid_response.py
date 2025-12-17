import strawberry

from app.graphql.v2.rbac.models.enums import (
    RbacPrivilegeOptionEnum,
    RbacPrivilegeTypeEnum,
    RbacResourceEnum,
)


@strawberry.type
class RbacPrivilegeResponse:
    privilege: RbacPrivilegeTypeEnum
    option: RbacPrivilegeOptionEnum


@strawberry.type
class RbacRolePermissionResponse:
    role_name: str
    privileges: list[RbacPrivilegeResponse]


@strawberry.type
class RbacGridResponse:
    resource: RbacResourceEnum
    roles: list[RbacRolePermissionResponse]
