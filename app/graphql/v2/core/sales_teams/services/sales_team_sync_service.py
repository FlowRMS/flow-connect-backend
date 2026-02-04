from decimal import Decimal
from uuid import UUID

from commons.db.v6.core.sales_teams.sales_team_member import SalesTeamMember
from commons.db.v6.core.territories.territory_split_rate import TerritorySplitRate

from app.graphql.v2.core.sales_teams.repositories.sales_team_member_repository import (
    SalesTeamMemberRepository,
)
from app.graphql.v2.core.sales_teams.repositories.sales_team_repository import (
    SalesTeamRepository,
)
from app.graphql.v2.core.territories.repositories.territory_split_rate_repository import (
    TerritorySplitRateRepository,
)


class SalesTeamSyncService:
    def __init__(
        self,
        sales_team_repository: SalesTeamRepository,
        member_repository: SalesTeamMemberRepository,
        split_rate_repository: TerritorySplitRateRepository,
    ) -> None:
        super().__init__()
        self.sales_team_repository = sales_team_repository
        self.member_repository = member_repository
        self.split_rate_repository = split_rate_repository

    async def get_territory_user_ids(self, territory_id: UUID) -> list[UUID]:
        split_rates = await self.split_rate_repository.get_by_territory(territory_id)
        return [rate.user_id for rate in split_rates]

    async def get_team_user_ids(self, sales_team_id: UUID) -> list[UUID]:
        return await self.member_repository.get_member_user_ids(sales_team_id)

    async def check_list_mismatch(
        self, sales_team_id: UUID, territory_id: UUID
    ) -> tuple[bool, list[UUID], list[UUID]]:
        team_users = set(await self.get_team_user_ids(sales_team_id))
        territory_users = set(await self.get_territory_user_ids(territory_id))

        has_mismatch = team_users != territory_users
        only_in_team = list(team_users - territory_users)
        only_in_territory = list(territory_users - team_users)

        return has_mismatch, only_in_team, only_in_territory

    async def sync_team_to_territory(
        self, sales_team_id: UUID, territory_id: UUID
    ) -> None:
        team_users = await self.get_team_user_ids(sales_team_id)

        _ = await self.split_rate_repository.delete_by_territory(territory_id)

        for position, user_id in enumerate(team_users):
            rate = TerritorySplitRate(
                user_id=user_id,
                split_rate=Decimal("0"),
                position=position,
            )
            rate.territory_id = territory_id
            _ = await self.split_rate_repository.create(rate)

    async def sync_territory_to_team(
        self, territory_id: UUID, sales_team_id: UUID
    ) -> None:
        territory_users = await self.get_territory_user_ids(territory_id)

        _ = await self.member_repository.delete_by_sales_team(sales_team_id)

        for position, user_id in enumerate(territory_users):
            member = SalesTeamMember(user_id=user_id, position=position)
            member.sales_team_id = sales_team_id
            _ = await self.member_repository.create(member)

    async def link_team_to_territory(
        self,
        sales_team_id: UUID,
        territory_id: UUID,
        sync_team_to_territory: bool,
    ) -> None:
        if sync_team_to_territory:
            await self.sync_team_to_territory(sales_team_id, territory_id)
        else:
            await self.sync_territory_to_team(territory_id, sales_team_id)

        team = await self.sales_team_repository.get_by_id(sales_team_id)
        if team:
            team.territory_id = territory_id
            _ = await self.sales_team_repository.update(team)
