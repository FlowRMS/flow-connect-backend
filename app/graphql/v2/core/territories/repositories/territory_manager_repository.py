from uuid import UUID

from commons.db.v6.core.territories.territory_manager import TerritoryManager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class TerritoryManagerRepository(BaseRepository[TerritoryManager]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, TerritoryManager)

    async def get_by_territory(self, territory_id: UUID) -> list[TerritoryManager]:
        stmt = (
            select(TerritoryManager)
            .where(TerritoryManager.territory_id == territory_id)
            .options(joinedload(TerritoryManager.user))
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def get_territories_for_user(self, user_id: UUID) -> list[TerritoryManager]:
        stmt = (
            select(TerritoryManager)
            .where(TerritoryManager.user_id == user_id)
            .options(joinedload(TerritoryManager.territory))
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def get_by_territory_and_user(
        self, territory_id: UUID, user_id: UUID
    ) -> TerritoryManager | None:
        stmt = select(TerritoryManager).where(
            TerritoryManager.territory_id == territory_id,
            TerritoryManager.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_managed_territory_ids(self, user_id: UUID) -> list[UUID]:
        stmt = select(TerritoryManager.territory_id).where(
            TerritoryManager.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
