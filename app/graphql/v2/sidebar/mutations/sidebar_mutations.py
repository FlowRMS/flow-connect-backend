from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6 import RbacRoleEnum

from app.graphql.inject import inject
from app.graphql.v2.sidebar.services import SidebarConfigurationService
from app.graphql.v2.sidebar.strawberry import (
    AssignSidebarToRoleInput,
    RoleSidebarAssignmentResponse,
    SaveSidebarConfigurationInput,
    SidebarConfigurationResponse,
)


@strawberry.type
class SidebarMutations:
    @strawberry.mutation
    @inject
    async def save_sidebar_configuration(
        self,
        input: SaveSidebarConfigurationInput,
        service: Injected[SidebarConfigurationService],
    ) -> SidebarConfigurationResponse:
        config = await service.save_configuration(input)
        return SidebarConfigurationResponse.from_model(config)

    @strawberry.mutation
    @inject
    async def delete_sidebar_configuration(
        self,
        id: UUID,
        service: Injected[SidebarConfigurationService],
    ) -> bool:
        return await service.delete_configuration(id)

    @strawberry.mutation
    @inject
    async def assign_sidebar_configuration_to_role(
        self,
        input: AssignSidebarToRoleInput,
        service: Injected[SidebarConfigurationService],
    ) -> RoleSidebarAssignmentResponse:
        assignment = await service.assign_to_role(
            role=input.role,
            configuration_id=input.configuration_id,
        )
        return RoleSidebarAssignmentResponse.from_model(assignment)

    @strawberry.mutation
    @inject
    async def remove_role_sidebar_assignment(
        self,
        role: RbacRoleEnum,
        service: Injected[SidebarConfigurationService],
    ) -> bool:
        return await service.remove_role_assignment(role)

    @strawberry.mutation
    @inject
    async def set_active_sidebar_configuration(
        self,
        configuration_id: UUID | None,
        service: Injected[SidebarConfigurationService],
    ) -> bool:
        return await service.set_active_configuration(configuration_id)
