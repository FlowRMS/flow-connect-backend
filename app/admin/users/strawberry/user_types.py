from dataclasses import dataclass
from uuid import UUID

import strawberry
from commons.db.v6.rbac.rbac_role_enum import RbacRoleEnum


@dataclass
class AdminUserData:
    id: UUID
    username: str
    first_name: str
    last_name: str
    email: str
    full_name: str
    enabled: bool
    role: RbacRoleEnum
    auth_provider_id: str
    inside: bool | None
    outside: bool | None
    tenant_id: UUID
    tenant_name: str
    tenant_url: str


@strawberry.type
class AdminUserType:
    id: UUID
    username: str
    first_name: str
    last_name: str
    email: str
    full_name: str
    enabled: bool
    role: RbacRoleEnum
    auth_provider_id: str
    inside: bool | None
    outside: bool | None
    tenant_id: UUID
    tenant_name: str
    tenant_url: str

    @classmethod
    def from_data(cls, data: AdminUserData) -> "AdminUserType":
        return cls(
            id=data.id,
            username=data.username,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            full_name=data.full_name,
            enabled=data.enabled,
            role=data.role,
            auth_provider_id=data.auth_provider_id,
            inside=data.inside,
            outside=data.outside,
            tenant_id=data.tenant_id,
            tenant_name=data.tenant_name,
            tenant_url=data.tenant_url,
        )

    @classmethod
    def from_data_list(cls, data_list: list[AdminUserData]) -> list["AdminUserType"]:
        return [cls.from_data(data) for data in data_list]
