from uuid import UUID

from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from commons.db.v6.fulfillment import FulfillmentOrder, FulfillmentOrderStatus

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class FulfillmentOrderRepository(BaseRepository[FulfillmentOrder]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, FulfillmentOrder)

    async def get_with_relations(self, order_id: UUID) -> FulfillmentOrder | None:
        stmt = (
            select(FulfillmentOrder)
            .options(
                selectinload(FulfillmentOrder.warehouse),
                selectinload(FulfillmentOrder.carrier),
                selectinload(FulfillmentOrder.line_items),
                selectinload(FulfillmentOrder.packing_boxes),
                selectinload(FulfillmentOrder.assignments),
                selectinload(FulfillmentOrder.activities),
            )
            .where(FulfillmentOrder.id == order_id)
        )
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
        stmt = select(FulfillmentOrder).options(
            selectinload(FulfillmentOrder.warehouse),
            selectinload(FulfillmentOrder.line_items),
        )

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
            build_count_query([
                FulfillmentOrderStatus.RELEASED,
                FulfillmentOrderStatus.PICKING,
                FulfillmentOrderStatus.PACKING,
                FulfillmentOrderStatus.SHIPPING,
            ])
        )

        completed_result = await self.session.execute(
            build_count_query([
                FulfillmentOrderStatus.SHIPPED,
                FulfillmentOrderStatus.DELIVERED,
                FulfillmentOrderStatus.COMMUNICATED,
            ])
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
