from uuid import UUID

from commons.db.v6.warehouse import FreightCategory
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class FreightCategoriesRepository(BaseRepository[FreightCategory]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            FreightCategory,
        )

    async def list_all_ordered(self) -> list[FreightCategory]:
        stmt = select(FreightCategory).order_by(FreightCategory.position)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_active_ordered(self) -> list[FreightCategory]:
        stmt = (
            select(FreightCategory)
            .where(FreightCategory.is_active == True)  # noqa: E712
            .order_by(FreightCategory.position)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_max_position(self) -> int:
        from sqlalchemy import func

        stmt = select(func.max(FreightCategory.position))
        result = await self.session.execute(stmt)
        max_position = result.scalar()
        return max_position if max_position is not None else 0

    async def reorder(self, ordered_ids: list[UUID]) -> list[FreightCategory]:
        """Reorder freight categories based on the provided ID list.

        Each category's position is set to its index in the list + 1.
        Uses negative temporary values to avoid unique constraint violation.
        """
        # First pass: set all positions to negative temporary values
        for idx, category_id in enumerate(ordered_ids):
            stmt = (
                update(FreightCategory)
                .where(FreightCategory.id == category_id)
                .values(position=-(idx + 1))
            )
            _ = await self.session.execute(stmt)

        await self.session.flush()

        # Second pass: set all positions to positive final values
        for idx, category_id in enumerate(ordered_ids):
            stmt = (
                update(FreightCategory)
                .where(FreightCategory.id == category_id)
                .values(position=idx + 1)
            )
            _ = await self.session.execute(stmt)

        await self.session.flush()
        return await self.list_all_ordered()
