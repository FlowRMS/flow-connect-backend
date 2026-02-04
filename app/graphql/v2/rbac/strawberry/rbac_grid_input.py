import strawberry
from commons.db.v6 import RbacResourceEnum

from app.graphql.v2.rbac.strawberry.rbac_grid_role_input import RbacGridRoleInput


@strawberry.input
class RbacGridInput:
    resource: RbacResourceEnum
    roles: list[RbacGridRoleInput]
