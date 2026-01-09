from uuid import UUID

import strawberry
from commons.db.v6.rbac.rbac_role_enum import RbacRoleEnum


@strawberry.input
class CreateAdminUserInput:
    tenant_id: UUID
    email: str
    first_name: str
    last_name: str
    role: RbacRoleEnum
    username: str | None = None
    enabled: bool = True
    inside: bool | None = None
    outside: bool | None = None
    visible: bool | None = True


@strawberry.input
class UpdateAdminUserInput:
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    username: str | None = None
    role: RbacRoleEnum | None = None
    enabled: bool | None = None
    inside: bool | None = None
    outside: bool | None = None
    visible: bool | None = None
