from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from commons.db.v6.fulfillment import FulfillmentOrderLineItem

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class FulfillmentLineRepository(BaseRepository[FulfillmentOrderLineItem]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, FulfillmentOrderLineItem)

    async def get_with_relations(
        self, line_item_id: UUID
    ) -> FulfillmentOrderLineItem | None:
        stmt = (
            select(FulfillmentOrderLineItem)
            .options(
                selectinload(FulfillmentOrderLineItem.product),
                selectinload(FulfillmentOrderLineItem.order_detail),
                selectinload(FulfillmentOrderLineItem.packing_box_items),
            )
            .where(FulfillmentOrderLineItem.id == line_item_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_fulfillment_order(
        self, fulfillment_order_id: UUID
    ) -> list[FulfillmentOrderLineItem]:
        stmt = (
            select(FulfillmentOrderLineItem)
            .options(selectinload(FulfillmentOrderLineItem.product))
            .where(
                FulfillmentOrderLineItem.fulfillment_order_id == fulfillment_order_id
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
