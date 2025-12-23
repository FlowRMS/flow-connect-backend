import strawberry
from aioinject import Injected

from app.admin.inject import admin_inject
from app.admin.tenants.services.tenant_creation_service import TenantCreationService
from app.admin.tenants.strawberry.tenant_input import CreateTenantInput
from app.admin.tenants.strawberry.tenant_response import (
    TenantCreationResultType,
    TenantType,
)


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
