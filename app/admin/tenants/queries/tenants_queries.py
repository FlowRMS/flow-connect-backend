from uuid import UUID

import strawberry
from aioinject import Injected

from app.admin.inject import admin_inject
from app.admin.tenants.services.tenant_creation_service import TenantCreationService
from app.admin.tenants.strawberry.tenant_response import TenantType


@strawberry.type
class TenantsQueries:
    @strawberry.field
    @admin_inject
    async def tenants(
        self,
        service: Injected[TenantCreationService],
    ) -> list[TenantType]:
        tenants = await service.list_tenants()
        return TenantType.from_model_list(tenants)

    @strawberry.field
    @admin_inject
    async def tenant(
        self,
        id: UUID,
        service: Injected[TenantCreationService],
    ) -> TenantType | None:
        tenant = await service.get_tenant(id)
        if not tenant:
            return None
        return TenantType.from_model(tenant)
