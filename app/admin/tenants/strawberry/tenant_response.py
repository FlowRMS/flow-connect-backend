from typing import Self
from uuid import UUID

import strawberry
from commons.db.models.tenant import Tenant


@strawberry.type
class TenantType:
    id: UUID
    name: str
    url: str
    database: str
    initialize: bool
    alembic_version: str

    @classmethod
    def from_model(cls, tenant: Tenant) -> Self:
        return cls(
            id=tenant.id,
            name=tenant.name,
            url=tenant.url,
            database=tenant.database,
            initialize=tenant.initialize,
            alembic_version=tenant.alembic_version,
        )

    @classmethod
    def from_model_list(cls, tenants: list[Tenant]) -> list[Self]:
        return [cls.from_model(t) for t in tenants]


@strawberry.type
class TenantCreationResultType:
    tenant: TenantType
    owner_workos_id: str
    workos_org_id: str
    success: bool
    message: str | None = None
