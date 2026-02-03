from uuid import UUID

from commons.db.v6.core.sales_teams.sales_team import SalesTeam
from commons.db.v6.core.sales_teams.sales_team_member import SalesTeamMember
from sqlalchemy.orm import joinedload

from app.errors.common_errors import NameAlreadyExistsError, NotFoundError
from app.graphql.v2.core.sales_teams.repositories.sales_team_member_repository import (
    SalesTeamMemberRepository,
)
from app.graphql.v2.core.sales_teams.repositories.sales_team_repository import (
    SalesTeamRepository,
)
from app.graphql.v2.core.sales_teams.strawberry.sales_team_input import SalesTeamInput


class SalesTeamService:
    def __init__(
        self,
        repository: SalesTeamRepository,
        member_repository: SalesTeamMemberRepository,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.member_repository = member_repository

    async def get_by_id(self, sales_team_id: UUID) -> SalesTeam:
        team = await self.repository.get_by_id(
            sales_team_id,
            options=[
                joinedload(SalesTeam.manager),
                joinedload(SalesTeam.territory),
                joinedload(SalesTeam.members),
                joinedload(SalesTeam.members).joinedload(SalesTeamMember.user),
            ],
        )
        if not team:
            raise NotFoundError(f"Sales team with id {sales_team_id} not found")
        return team

    async def get_by_id_optional(self, sales_team_id: UUID) -> SalesTeam | None:
        try:
            return await self.get_by_id(sales_team_id)
        except NotFoundError:
            return None

    async def create(self, input: SalesTeamInput) -> SalesTeam:
        if await self.repository.name_exists(input.name):
            raise NameAlreadyExistsError(f"Sales team '{input.name}' already exists")

        team = await self.repository.create(input.to_orm_model())
        return await self.get_by_id(team.id)

    async def update(self, sales_team_id: UUID, input: SalesTeamInput) -> SalesTeam:
        if await self.repository.name_exists(input.name, exclude_id=sales_team_id):
            raise NameAlreadyExistsError(f"Sales team '{input.name}' already exists")

        existing_members = await self.member_repository.get_by_sales_team(sales_team_id)

        team = input.to_orm_model()
        team.id = sales_team_id
        team.members = existing_members
        _ = await self.repository.update(team)
        return await self.get_by_id(sales_team_id)

    async def delete(self, sales_team_id: UUID) -> bool:
        if not await self.repository.exists(sales_team_id):
            raise NotFoundError(f"Sales team with id {sales_team_id} not found")
        return await self.repository.delete(sales_team_id)

    async def get_all_active(self) -> list[SalesTeam]:
        return await self.repository.get_all_active_with_relations()

    async def add_member(
        self, sales_team_id: UUID, user_id: UUID, position: int = 0
    ) -> SalesTeam:
        if not await self.repository.exists(sales_team_id):
            raise NotFoundError(f"Sales team with id {sales_team_id} not found")

        existing = await self.member_repository.get_by_sales_team_and_user(
            sales_team_id, user_id
        )
        if not existing:
            member = SalesTeamMember(user_id=user_id, position=position)
            member.sales_team_id = sales_team_id
            _ = await self.member_repository.create(member)

        return await self.get_by_id(sales_team_id)

    async def remove_member(self, sales_team_id: UUID, user_id: UUID) -> SalesTeam:
        member = await self.member_repository.get_by_sales_team_and_user(
            sales_team_id, user_id
        )
        if not member:
            raise NotFoundError("Team member not found")
        _ = await self.member_repository.delete(member.id)
        return await self.get_by_id(sales_team_id)

    async def get_team_member_user_ids(self, sales_team_id: UUID) -> list[UUID]:
        return await self.member_repository.get_member_user_ids(sales_team_id)

    async def unlink_territory(self, sales_team_id: UUID) -> SalesTeam:
        team = await self.get_by_id(sales_team_id)
        team.territory_id = None
        _ = await self.repository.update(team)
        return await self.get_by_id(sales_team_id)
