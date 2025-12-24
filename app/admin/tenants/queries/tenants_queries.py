from uuid import UUID

import strawberry
from aioinject import Injected

from app.admin.inject import admin_inject
from app.admin.tenants.services.tenant_creation_service import TenantCreationService
from app.admin.tenants.strawberry.tenant_response import TenantType
from app.admin.users.services.admin_user_service import AdminUserService
from app.admin.users.strawberry.user_types import AdminUserType


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

    @strawberry.field
    @admin_inject
    async def admin_users(
        self,
        service: Injected[AdminUserService],
        tenant_id: UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AdminUserType]:
        users = await service.list_all_users(
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
        )
        return AdminUserType.from_data_list(users)

    @strawberry.field
    @admin_inject
    async def admin_user(
        self,
        tenant_id: UUID,
        user_id: UUID,
        service: Injected[AdminUserService],
    ) -> AdminUserType | None:
        user = await service.get_user(tenant_id=tenant_id, user_id=user_id)
        if not user:
            return None
        return AdminUserType.from_data(user)
