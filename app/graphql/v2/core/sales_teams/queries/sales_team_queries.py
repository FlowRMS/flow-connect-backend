from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.sales_teams.services.sales_team_service import SalesTeamService
from app.graphql.v2.core.sales_teams.services.sales_team_sync_service import (
    SalesTeamSyncService,
)
from app.graphql.v2.core.sales_teams.strawberry.sales_team_response import (
    MismatchCheckResponse,
    SalesTeamResponse,
)
from app.graphql.v2.core.users.services.user_service import UserService
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class SalesTeamQueries:
    @strawberry.field
    @inject
    async def sales_team(
        self,
        id: UUID,
        service: Injected[SalesTeamService],
    ) -> SalesTeamResponse | None:
        team = await service.get_by_id_optional(id)
        return SalesTeamResponse.from_orm_model_optional(team)

    @strawberry.field
    @inject
    async def all_sales_teams(
        self,
        service: Injected[SalesTeamService],
    ) -> list[SalesTeamResponse]:
        teams = await service.get_all_active()
        return SalesTeamResponse.from_orm_model_list(teams)

    @strawberry.field
    @inject
    async def check_team_territory_mismatch(
        self,
        sales_team_id: UUID,
        territory_id: UUID,
        sync_service: Injected[SalesTeamSyncService],
        user_service: Injected[UserService],
    ) -> MismatchCheckResponse:
        (
            has_mismatch,
            only_in_team_ids,
            only_in_territory_ids,
        ) = await sync_service.check_list_mismatch(sales_team_id, territory_id)

        team_users = await user_service.get_by_ids(only_in_team_ids)
        only_in_team = [UserResponse.from_orm_model(u) for u in team_users]

        territory_users = await user_service.get_by_ids(only_in_territory_ids)
        only_in_territory = [UserResponse.from_orm_model(u) for u in territory_users]

        return MismatchCheckResponse(
            has_mismatch=has_mismatch,
            only_in_team=only_in_team,
            only_in_territory=only_in_territory,
        )
