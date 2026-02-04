import strawberry
from aioinject import Injected
from commons.db.v6.rbac.rbac_role_enum import RbacRoleEnum
from strawberry.permission import PermissionExtension

from app.core.middleware.route_extension import RolePermissionAccess
from app.graphql.inject import inject
from app.graphql.v2.rbac.services.rbac_service import RbacService
from app.graphql.v2.rbac.strawberry.rbac_grid_input import RbacGridInput
from app.graphql.v2.rbac.strawberry.rbac_grid_response import (
    RbacGridResponse,
    RbacRoleSettingResponse,
)
from app.graphql.v2.rbac.strawberry.update_commission_visibility_input import (
    UpdateCommissionVisibilityInput,
)


@strawberry.type
class RbacMutations:
    @strawberry.mutation(
        extensions=[
            PermissionExtension(
                permissions=[
                    RolePermissionAccess(
                        [RbacRoleEnum.ADMINISTRATOR, RbacRoleEnum.OWNER]
                    )
                ]
            )
        ]
    )
    @inject
    async def update_rbac_grid(
        self,
        rbac_grid: list[RbacGridInput],
        service: Injected[RbacService],
    ) -> list[RbacGridResponse]:
        return await service.update_rbac_grid(rbac_grid)

    @strawberry.mutation(
        extensions=[
            PermissionExtension(
                permissions=[
                    RolePermissionAccess(
                        [RbacRoleEnum.ADMINISTRATOR, RbacRoleEnum.OWNER]
                    )
                ]
            )
        ]
    )
    @inject
    async def update_commission_visibility(
        self,
        input: UpdateCommissionVisibilityInput,
        service: Injected[RbacService],
    ) -> RbacRoleSettingResponse:
        role_setting = await service.update_commission_visibility(
            input.role, input.commission
        )
        return RbacRoleSettingResponse(
            role=role_setting.role,
            commission=role_setting.commission,
        )
