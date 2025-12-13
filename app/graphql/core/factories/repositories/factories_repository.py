from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.core.factories.models import FactoryV2, ManufacturerOrder
from app.graphql.links.models.entity_type import EntityType


class FactoriesRepository(BaseRepository[FactoryV2]):
    """Repository for Factories entity."""

    entity_type = EntityType.FACTORY

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, FactoryV2)

    async def search_by_title(
        self, search_term: str, published: bool = True, limit: int = 20
    ) -> list[FactoryV2]:
        """
        Search factories by title using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against title
            published: Filter by published status (default: True)
            limit: Maximum number of factories to return (default: 20)

        Returns:
            List of FactoryV2 objects matching the search criteria
        """
        stmt = (
            select(FactoryV2)
            .where(FactoryV2.title.ilike(f"%{search_term}%"))
            .limit(limit)
        )

        if published is not None:
            stmt = stmt.where(FactoryV2.published == published)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_manufacturer_order(self) -> dict[UUID, int]:
        """
        Get the current manufacturer order.

        Returns:
            Dictionary mapping factory_id to sort_order
        """
        stmt = select(ManufacturerOrder)
        result = await self.session.execute(stmt)
        orders = result.scalars().all()
        return {order.factory_id: order.sort_order for order in orders}

    async def update_manufacturer_order(self, factory_ids: list[UUID]) -> int:
        """
        Update the manufacturer order.

        Args:
            factory_ids: List of factory IDs in the desired order

        Returns:
            Number of manufacturers updated
        """
        # Delete all existing orders
        _ = await self.session.execute(delete(ManufacturerOrder))

        # Insert new orders
        for index, factory_id in enumerate(factory_ids):
            order = ManufacturerOrder(factory_id=factory_id, sort_order=index)
            self.session.add(order)

        await self.session.commit()
        return len(factory_ids)

    async def search_by_title_ordered(
        self, search_term: str, published: bool = True, limit: int = 20
    ) -> list[FactoryV2]:
        """
        Search factories by title with custom sort order applied.

        Args:
            search_term: The search term to match against title
            published: Filter by published status (default: True)
            limit: Maximum number of factories to return (default: 20)

        Returns:
            List of FactoryV2 objects sorted by custom order, then by title
        """
        # Get factories
        factories = await self.search_by_title(search_term, published, limit)

        # Get the order mapping
        order_map = await self.get_manufacturer_order()

        # Sort: factories with order first (by sort_order), then unordered (by title)
        def sort_key(factory: FactoryV2) -> tuple[int, int, str]:
            if factory.id in order_map:
                return (0, order_map[factory.id], factory.title)
            return (1, 0, factory.title)

        return sorted(factories, key=sort_key)
