"""Repository for container type operations."""

from uuid import UUID

from commons.db.v6 import ContainerType
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class ContainerTypesRepository(BaseRepository[ContainerType]):
    """Repository for ContainerType entity."""

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            ContainerType,
        )

    async def list_all_ordered(self) -> list[ContainerType]:
        """Get all container types ordered by display order."""
        stmt = select(ContainerType).order_by(ContainerType.order)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_max_order(self) -> int:
        """Get the maximum order value."""
        from sqlalchemy import func

        stmt = select(func.max(ContainerType.order))
        result = await self.session.execute(stmt)
        max_order = result.scalar()
        return max_order if max_order is not None else 0

    async def reorder(self, ordered_ids: list[UUID]) -> list[ContainerType]:
        """Reorder container types based on the provided ID list.

        Each container type's order is set to its index in the list + 1.
        Uses negative temporary values to avoid unique constraint violation.
        """
        # First pass: set all orders to negative temporary values
        for idx, container_id in enumerate(ordered_ids):
            stmt = (
                update(ContainerType)
                .where(ContainerType.id == container_id)
                .values(order=-(idx + 1))
            )
            await self.session.execute(stmt)

        await self.session.flush()

        # Second pass: set all orders to positive final values
        for idx, container_id in enumerate(ordered_ids):
            stmt = (
                update(ContainerType)
                .where(ContainerType.id == container_id)
                .values(order=idx + 1)
            )
            await self.session.execute(stmt)

        await self.session.flush()
        return await self.list_all_ordered()
