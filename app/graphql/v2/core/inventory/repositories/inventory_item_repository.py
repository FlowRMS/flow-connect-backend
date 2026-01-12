from uuid import UUID

from commons.db.v6.warehouse.inventory.inventory_item import InventoryItem
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.constants import DEFAULT_QUERY_LIMIT, DEFAULT_QUERY_OFFSET
from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class InventoryItemRepository(BaseRepository[InventoryItem]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            InventoryItem,
        )

    async def find_by_inventory_id(
        self,
        inventory_id: UUID,
        limit: int = DEFAULT_QUERY_LIMIT,
        offset: int = DEFAULT_QUERY_OFFSET,
    ) -> list[InventoryItem]:
        stmt = (
            select(InventoryItem)
            .where(InventoryItem.inventory_id == inventory_id)
            .options(joinedload(InventoryItem.location))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
