from typing import Any
from uuid import UUID

from commons.db.v6.commission.orders.order import Order
from commons.db.v6.core import Product
from commons.db.v6.fulfillment import (
    FulfillmentOrder,
    FulfillmentOrderLineItem,
    FulfillmentOrderStatus,
)
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class FulfillmentOrderRepository(BaseRepository[FulfillmentOrder]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, FulfillmentOrder)

    @property
    def base_query(self) -> Select[tuple[FulfillmentOrder]]:
        """Base query with comprehensive eager loading for detail views."""
        return select(FulfillmentOrder).options(
            joinedload(FulfillmentOrder.warehouse),
            joinedload(FulfillmentOrder.carrier),
            joinedload(FulfillmentOrder.ship_to_address),
            joinedload(FulfillmentOrder.order).joinedload(Order.sold_to_customer),
            selectinload(FulfillmentOrder.line_items).options(
                joinedload(FulfillmentOrderLineItem.product).options(
                    joinedload(Product.uom),
                    joinedload(Product.factory),
                ),
                joinedload(FulfillmentOrderLineItem.order_detail),
            ),
            selectinload(FulfillmentOrder.packing_boxes),
            selectinload(FulfillmentOrder.assignments),
            selectinload(FulfillmentOrder.activities),
            selectinload(FulfillmentOrder.documents),
        )

    @property
    def list_query(self) -> Select[tuple[FulfillmentOrder]]:
        """Lighter query for list endpoints - no nested collections."""
        return select(FulfillmentOrder).options(
            joinedload(FulfillmentOrder.warehouse),
            joinedload(FulfillmentOrder.carrier),
            joinedload(FulfillmentOrder.order).joinedload(Order.sold_to_customer),
        )

    async def get_with_relations(self, order_id: UUID) -> FulfillmentOrder | None:
        stmt = self.base_query.where(FulfillmentOrder.id == order_id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def list_orders(
        self,
        warehouse_id: UUID | None = None,
        status: list[FulfillmentOrderStatus] | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[FulfillmentOrder]:
        stmt = self.list_query

        if warehouse_id:
            stmt = stmt.where(FulfillmentOrder.warehouse_id == warehouse_id)

        if status:
            stmt = stmt.where(FulfillmentOrder.status.in_(status))

        if search:
            stmt = stmt.where(
                FulfillmentOrder.fulfillment_order_number.ilike(f"%{search}%")
            )

        stmt = stmt.order_by(FulfillmentOrder.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def get_stats(self, warehouse_id: UUID | None = None) -> dict[str, int]:
        def build_count_query(statuses: list[FulfillmentOrderStatus]) -> Select[Any]:
            query = select(func.count(FulfillmentOrder.id)).where(
                FulfillmentOrder.status.in_(statuses)
            )
            if warehouse_id:
                query = query.where(FulfillmentOrder.warehouse_id == warehouse_id)
            return query

        pending_result = await self.session.execute(
            build_count_query([FulfillmentOrderStatus.PENDING])
        )

        in_progress_result = await self.session.execute(
            build_count_query(
                [
                    FulfillmentOrderStatus.RELEASED,
                    FulfillmentOrderStatus.PICKING,
                    FulfillmentOrderStatus.PACKING,
                    FulfillmentOrderStatus.SHIPPING,
                ]
            )
        )

        completed_result = await self.session.execute(
            build_count_query(
                [
                    FulfillmentOrderStatus.SHIPPED,
                    FulfillmentOrderStatus.DELIVERED,
                    FulfillmentOrderStatus.COMMUNICATED,
                ]
            )
        )

        backorder_result = await self.session.execute(
            build_count_query([FulfillmentOrderStatus.BACKORDER_REVIEW])
        )

        return {
            "pending": pending_result.scalar() or 0,
            "in_progress": in_progress_result.scalar() or 0,
            "completed": completed_result.scalar() or 0,
            "backorder": backorder_result.scalar() or 0,
        }

    async def get_next_order_number(self) -> int:
        stmt = select(func.count(FulfillmentOrder.id))
        result = await self.session.execute(stmt)
        return (result.scalar() or 0) + 1
