import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.sidebar.services import (
    EffectiveSidebarService,
    SidebarConfigurationService,
)
from app.graphql.v2.sidebar.strawberry import (
    ConfigurableSidebarResponse,
    EffectiveSidebarResponse,
    RoleSidebarAssignmentResponse,
    SidebarConfigurationResponse,
)


@strawberry.type
class SidebarQueries:
    @strawberry.field
    @inject
    async def admin_sidebar_configurations(
        self,
        service: Injected[SidebarConfigurationService],
    ) -> list[SidebarConfigurationResponse]:
        configs = await service.get_admin_configurations()
        return [SidebarConfigurationResponse.from_model(c) for c in configs]

    @strawberry.field
    @inject
    async def user_sidebar_configurations(
        self,
        service: Injected[SidebarConfigurationService],
    ) -> list[SidebarConfigurationResponse]:
        configs = await service.get_user_configurations()
        return [SidebarConfigurationResponse.from_model(c) for c in configs]

    @strawberry.field
    @inject
    async def role_sidebar_assignments(
        self,
        service: Injected[SidebarConfigurationService],
    ) -> list[RoleSidebarAssignmentResponse]:
        assignments = await service.get_role_assignments()
        return [RoleSidebarAssignmentResponse.from_model(a) for a in assignments]

    @strawberry.field
    @inject
    async def effective_sidebar(
        self,
        service: Injected[EffectiveSidebarService],
    ) -> EffectiveSidebarResponse:
        sidebar = await service.get_effective_sidebar()
        return EffectiveSidebarResponse.from_dataclass(sidebar)

    @strawberry.field
    @inject
    async def configurable_sidebar(
        self,
        service: Injected[EffectiveSidebarService],
    ) -> ConfigurableSidebarResponse:
        hidden_items, _ = await service.get_configurable_sidebar()
        return ConfigurableSidebarResponse(admin_hidden_items=hidden_items)
