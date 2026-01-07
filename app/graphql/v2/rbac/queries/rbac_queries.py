import strawberry
from aioinject import Injected
from commons.db.v6 import RbacResourceEnum

from app.graphql.inject import inject
from app.graphql.v2.rbac.services.rbac_service import RbacService
from app.graphql.v2.rbac.strawberry.rbac_grid_response import (
    RbacGridResponse,
    RbacRoleSettingResponse,
)
from app.graphql.v2.rbac.strawberry.user_rbac_response import UserRbac


@strawberry.type
class RbacQueries:
    @strawberry.field
    @inject
    async def get_rbac_grid(
        self,
        service: Injected[RbacService],
    ) -> list[RbacGridResponse]:
        return await service.get_rbac_grid()

    @strawberry.field
    @inject
    async def get_user_rbac(
        self,
        resource: RbacResourceEnum,
        service: Injected[RbacService],
    ) -> UserRbac:
        return await service.get_user_rbac(resource)

    @strawberry.field
    @inject
    async def get_role_settings(
        self,
        service: Injected[RbacService],
    ) -> list[RbacRoleSettingResponse]:
        role_settings = await service.get_all_role_settings()
        return [
            RbacRoleSettingResponse(role=rs.role, commission=rs.commission)
            for rs in role_settings
        ]
