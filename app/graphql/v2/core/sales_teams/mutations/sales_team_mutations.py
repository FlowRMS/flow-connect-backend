from enum import Enum
from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.sales_teams.services.sales_team_service import SalesTeamService
from app.graphql.v2.core.sales_teams.services.sales_team_sync_service import (
    SalesTeamSyncService,
)
from app.graphql.v2.core.sales_teams.strawberry.sales_team_input import SalesTeamInput
from app.graphql.v2.core.sales_teams.strawberry.sales_team_response import (
    SalesTeamResponse,
)


@strawberry.enum
class SyncDirection(Enum):
    TEAM_TO_TERRITORY = "TEAM_TO_TERRITORY"
    TERRITORY_TO_TEAM = "TERRITORY_TO_TEAM"


@strawberry.type
class SalesTeamMutations:
    @strawberry.mutation
    @inject
    async def create_sales_team(
        self,
        input: SalesTeamInput,
        service: Injected[SalesTeamService],
    ) -> SalesTeamResponse:
        team = await service.create(input)
        return SalesTeamResponse.from_orm_model(team)

    @strawberry.mutation
    @inject
    async def update_sales_team(
        self,
        id: UUID,
        input: SalesTeamInput,
        service: Injected[SalesTeamService],
    ) -> SalesTeamResponse:
        team = await service.update(id, input)
        return SalesTeamResponse.from_orm_model(team)

    @strawberry.mutation
    @inject
    async def delete_sales_team(
        self,
        id: UUID,
        service: Injected[SalesTeamService],
    ) -> bool:
        return await service.delete(id)

    @strawberry.mutation
    @inject
    async def add_sales_team_member(
        self,
        sales_team_id: UUID,
        user_id: UUID,
        service: Injected[SalesTeamService],
        position: int = 0,
    ) -> SalesTeamResponse:
        team = await service.add_member(sales_team_id, user_id, position)
        return SalesTeamResponse.from_orm_model(team)

    @strawberry.mutation
    @inject
    async def remove_sales_team_member(
        self,
        sales_team_id: UUID,
        user_id: UUID,
        service: Injected[SalesTeamService],
    ) -> SalesTeamResponse:
        team = await service.remove_member(sales_team_id, user_id)
        return SalesTeamResponse.from_orm_model(team)

    @strawberry.mutation
    @inject
    async def link_sales_team_to_territory(
        self,
        sales_team_id: UUID,
        territory_id: UUID,
        sync_direction: SyncDirection,
        service: Injected[SalesTeamService],
        sync_service: Injected[SalesTeamSyncService],
    ) -> SalesTeamResponse:
        sync_team_to_territory = sync_direction == SyncDirection.TEAM_TO_TERRITORY
        await sync_service.link_team_to_territory(
            sales_team_id, territory_id, sync_team_to_territory
        )
        team = await service.get_by_id(sales_team_id)
        return SalesTeamResponse.from_orm_model(team)

    @strawberry.mutation
    @inject
    async def unlink_sales_team_from_territory(
        self,
        sales_team_id: UUID,
        service: Injected[SalesTeamService],
    ) -> SalesTeamResponse:
        team = await service.unlink_territory(sales_team_id)
        return SalesTeamResponse.from_orm_model(team)
