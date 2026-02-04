from uuid import UUID

from commons.db.v6.core.sales_teams.sales_team_member import SalesTeamMember
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class SalesTeamMemberRepository(BaseRepository[SalesTeamMember]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, SalesTeamMember)

    async def get_by_sales_team(self, sales_team_id: UUID) -> list[SalesTeamMember]:
        stmt = (
            select(SalesTeamMember)
            .where(SalesTeamMember.sales_team_id == sales_team_id)
            .options(joinedload(SalesTeamMember.user))
            .order_by(SalesTeamMember.position)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def get_by_sales_team_and_user(
        self, sales_team_id: UUID, user_id: UUID
    ) -> SalesTeamMember | None:
        stmt = select(SalesTeamMember).where(
            SalesTeamMember.sales_team_id == sales_team_id,
            SalesTeamMember.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_teams_for_user(self, user_id: UUID) -> list[SalesTeamMember]:
        stmt = (
            select(SalesTeamMember)
            .where(SalesTeamMember.user_id == user_id)
            .options(joinedload(SalesTeamMember.sales_team))
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def delete_by_sales_team(self, sales_team_id: UUID) -> int:
        members = await self.get_by_sales_team(sales_team_id)
        for member in members:
            await self.session.delete(member)
        await self.session.flush()
        return len(members)

    async def get_member_user_ids(self, sales_team_id: UUID) -> list[UUID]:
        stmt = select(SalesTeamMember.user_id).where(
            SalesTeamMember.sales_team_id == sales_team_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
