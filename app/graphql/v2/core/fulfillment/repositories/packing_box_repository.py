from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from commons.db.v6.fulfillment import PackingBox, PackingBoxItem

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class PackingBoxRepository(BaseRepository[PackingBox]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, PackingBox)

    async def get_with_items(self, box_id: UUID) -> PackingBox | None:
        stmt = (
            select(PackingBox)
            .options(
                selectinload(PackingBox.items),
                selectinload(PackingBox.container_type),
            )
            .where(PackingBox.id == box_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_fulfillment_order(
        self, fulfillment_order_id: UUID
    ) -> list[PackingBox]:
        stmt = (
            select(PackingBox)
            .options(selectinload(PackingBox.items))
            .where(PackingBox.fulfillment_order_id == fulfillment_order_id)
            .order_by(PackingBox.box_number)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_next_box_number(self, fulfillment_order_id: UUID) -> int:
        stmt = (
            select(func.coalesce(func.max(PackingBox.box_number), 0))
            .where(PackingBox.fulfillment_order_id == fulfillment_order_id)
        )
        result = await self.session.execute(stmt)
        return (result.scalar() or 0) + 1


class PackingBoxItemRepository(BaseRepository[PackingBoxItem]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, PackingBoxItem)

    async def get_by_box_and_line_item(
        self, box_id: UUID, line_item_id: UUID
    ) -> PackingBoxItem | None:
        stmt = select(PackingBoxItem).where(
            PackingBoxItem.packing_box_id == box_id,
            PackingBoxItem.fulfillment_line_item_id == line_item_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_box(self, box_id: UUID) -> list[PackingBoxItem]:
        stmt = select(PackingBoxItem).where(PackingBoxItem.packing_box_id == box_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
