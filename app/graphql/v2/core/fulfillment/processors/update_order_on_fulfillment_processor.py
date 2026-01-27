from decimal import Decimal
from uuid import UUID

from commons.db.v6.commission.orders import Order, OrderHeaderStatus, OrderStatus
from commons.db.v6.fulfillment import FulfillmentOrder
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


class UpdateOrderOnFulfillmentProcessor:
    """Updates Order/OrderDetail status when fulfillment shipping completes."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    async def process_fulfillment_shipped(
        self, fulfillment_order: FulfillmentOrder
    ) -> Order | None:
        """Process status updates when a FulfillmentOrder is shipped."""
        order = await self._get_order_with_details(fulfillment_order.order_id)
        if not order:
            logger.warning(f"Order {fulfillment_order.order_id} not found")
            return None

        self._update_order_detail_statuses(order, fulfillment_order)
        self._update_order_status(order)
        await self.session.flush()
        return order

    async def _get_order_with_details(self, order_id: UUID) -> Order | None:
        result = await self.session.execute(
            select(Order).options(joinedload(Order.details)).where(Order.id == order_id)
        )
        return result.unique().scalar_one_or_none()

    def _update_order_detail_statuses(
        self, order: Order, fulfillment_order: FulfillmentOrder
    ) -> None:
        """Update OrderDetail statuses based on shipped quantities."""
        # Build mapping: order_detail_id -> shipped_qty
        shipped_by_detail: dict[UUID, Decimal] = {}
        for line_item in fulfillment_order.line_items:
            if line_item.order_detail_id:
                shipped_by_detail[line_item.order_detail_id] = (
                    shipped_by_detail.get(line_item.order_detail_id, Decimal("0"))
                    + line_item.shipped_qty
                )

        for detail in order.details:
            shipped_qty = shipped_by_detail.get(detail.id, Decimal("0"))
            if shipped_qty > 0:
                detail.shipping_balance = max(
                    Decimal("0"), detail.shipping_balance - shipped_qty
                )
                detail.status = self._calculate_detail_status(
                    detail.shipping_balance, detail.total
                )
                logger.info(
                    f"Updated OrderDetail {detail.id}: "
                    f"shipped={shipped_qty}, balance={detail.shipping_balance}, "
                    f"status={detail.status.name}"
                )

    def _calculate_detail_status(
        self, shipping_balance: Decimal, order_total: Decimal
    ) -> OrderStatus:
        """Calculate OrderDetail status based on shipping balance."""
        if shipping_balance < Decimal("0.00"):
            return OrderStatus.OVER_SHIPPED
        elif shipping_balance.quantize(Decimal("0.01")) <= Decimal("0.00").quantize(
            Decimal("0.01")
        ):
            return OrderStatus.SHIPPED_COMPLETE
        elif shipping_balance == order_total:
            return OrderStatus.OPEN
        else:
            return OrderStatus.PARTIAL_SHIPPED

    def _update_order_status(self, order: Order) -> None:
        """Update overall Order status based on all OrderDetail statuses."""
        if not order.details:
            return

        statuses = [d.status for d in order.details]

        if all(s == OrderStatus.OPEN for s in statuses):
            order.status = OrderStatus.OPEN
        elif all(s == OrderStatus.SHIPPED_COMPLETE for s in statuses):
            order.status = OrderStatus.SHIPPED_COMPLETE
            if order.header_status not in (
                OrderHeaderStatus.CANCELLED,
                OrderHeaderStatus.CLOSED,
            ):
                order.header_status = OrderHeaderStatus.CLOSED
        elif any(s == OrderStatus.OVER_SHIPPED for s in statuses):
            order.status = OrderStatus.OVER_SHIPPED
        else:
            order.status = OrderStatus.PARTIAL_SHIPPED

        logger.info(f"Updated Order {order.id} status to {order.status.name}")
