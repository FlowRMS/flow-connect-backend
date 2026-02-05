import strawberry
from commons.db.v6 import RbacRoleEnum

from app.graphql.v2.rbac.strawberry.rbac_grid_role_privilege_input import (
    RbacGridRolePrivilegeInput,
)


@strawberry.input
class RbacGridRoleInput:
    role: RbacRoleEnum
    privileges: list[RbacGridRolePrivilegeInput]
