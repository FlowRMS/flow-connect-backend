from uuid import UUID

import strawberry
from aioinject import Injected

from app.admin.inject import admin_inject
from app.admin.tenants.services.tenant_creation_service import TenantCreationService
from app.admin.tenants.strawberry.tenant_input import CreateTenantInput
from app.admin.tenants.strawberry.tenant_response import (
    TenantCreationResultType,
    TenantType,
)
from app.admin.users.services.admin_user_service import AdminUserService
from app.admin.users.strawberry.user_inputs import (
    CreateAdminUserInput,
    UpdateAdminUserInput,
)
from app.admin.users.strawberry.user_types import AdminUserType


@strawberry.type
class TenantsMutations:
    @strawberry.mutation
    @admin_inject
    async def create_tenant(
        self,
        input: CreateTenantInput,
        service: Injected[TenantCreationService],
    ) -> TenantCreationResultType:
        result = await service.create_tenant(
            name=input.name,
            owner_email=input.owner_email,
        )
        return TenantCreationResultType(
            tenant=TenantType.from_model(result.tenant),
            owner_workos_id=result.owner_workos_id,
            workos_org_id=result.workos_org_id,
            success=result.success,
            message=result.message,
        )

    @strawberry.mutation
    @admin_inject
    async def create_admin_user(
        self,
        input: CreateAdminUserInput,
        service: Injected[AdminUserService],
    ) -> AdminUserType:
        user = await service.create_user(input)
        return AdminUserType.from_data(user)

    @strawberry.mutation
    @admin_inject
    async def update_admin_user(
        self,
        tenant_id: UUID,
        user_id: UUID,
        input: UpdateAdminUserInput,
        service: Injected[AdminUserService],
    ) -> AdminUserType:
        user = await service.update_user(
            tenant_id=tenant_id,
            user_id=user_id,
            input=input,
        )
        return AdminUserType.from_data(user)
