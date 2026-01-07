import strawberry
from aioinject import Injected
from commons.db.v6.rbac.rbac_role_enum import RbacRoleEnum
from strawberry.permission import PermissionExtension

from app.core.middleware.route_extension import RolePermissionAccess
from app.graphql.inject import inject
from app.graphql.organizations.services.organization_service import OrganizationService
from app.graphql.organizations.strawberry.organization_inputs import OrganizationInput
from app.graphql.organizations.strawberry.organization_types import OrganizationType


@strawberry.type
class OrganizationsMutations:
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
    async def create_organization(
        self,
        input: OrganizationInput,
        service: Injected[OrganizationService],
    ) -> OrganizationType:
        org = await service.create_organization(input)
        return OrganizationType.from_orm_model(org)

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
    async def update_organization(
        self,
        input: OrganizationInput,
        service: Injected[OrganizationService],
    ) -> OrganizationType:
        org = await service.update_organization(input)
        return OrganizationType.from_orm_model(org)
