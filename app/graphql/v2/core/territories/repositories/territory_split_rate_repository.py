from uuid import UUID

from commons.db.v6.core.territories.territory_split_rate import TerritorySplitRate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class TerritorySplitRateRepository(BaseRepository[TerritorySplitRate]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, TerritorySplitRate)

    async def get_by_territory(self, territory_id: UUID) -> list[TerritorySplitRate]:
        stmt = (
            select(TerritorySplitRate)
            .where(TerritorySplitRate.territory_id == territory_id)
            .options(joinedload(TerritorySplitRate.user))
            .order_by(TerritorySplitRate.position)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def delete_by_territory(self, territory_id: UUID) -> int:
        splits = await self.get_by_territory(territory_id)
        for split in splits:
            await self.session.delete(split)
        await self.session.flush()
        return len(splits)
