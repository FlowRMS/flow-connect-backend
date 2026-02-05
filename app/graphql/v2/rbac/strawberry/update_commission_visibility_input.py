import strawberry
from commons.db.v6 import RbacRoleEnum


@strawberry.input
class UpdateCommissionVisibilityInput:
    role: RbacRoleEnum
    commission: bool
