from decimal import Decimal
from uuid import UUID

from commons.db.v6.commission import CreditDetail, InvoiceDetail
from commons.db.v6.commission.orders import Order, OrderHeaderStatus, OrderStatus
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.processors import BaseProcessor, EntityContext, RepositoryEvent


class RecalculateOrderStatusProcessor(BaseProcessor[Order]):
    """
    Recalculates order detail statuses and overall order status when an order is updated.

    When order details are modified (e.g., quantity or total changes), this processor
    recalculates shipping_balance based on existing invoiced/credited amounts and
    updates statuses accordingly (OPEN, PARTIAL_SHIPPED, SHIPPED_COMPLETE, OVER_SHIPPED).
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_UPDATE]

    async def process(self, context: EntityContext[Order]) -> None:
        order = context.entity

        if not order.details:
            return

        await self._recalculate_detail_statuses(order)
        self._update_order_status(order)

    async def _get_invoiced_totals_for_order(
        self, order_detail_ids: list[UUID]
    ) -> dict[UUID, Decimal]:
        if not order_detail_ids:
            return {}

        result = await self.session.execute(
            select(
                InvoiceDetail.order_detail_id,
                func.coalesce(func.sum(InvoiceDetail.total), Decimal("0")).label(
                    "total"
                ),
            )
            .where(InvoiceDetail.order_detail_id.in_(order_detail_ids))
            .group_by(InvoiceDetail.order_detail_id)
        )
        return {row.order_detail_id: row.total for row in result.fetchall()}

    async def _get_credited_totals_for_order(
        self, order_detail_ids: list[UUID]
    ) -> dict[UUID, Decimal]:
        if not order_detail_ids:
            return {}

        result = await self.session.execute(
            select(
                CreditDetail.order_detail_id,
                func.coalesce(func.sum(CreditDetail.total), Decimal("0")).label(
                    "total"
                ),
            )
            .where(CreditDetail.order_detail_id.in_(order_detail_ids))
            .group_by(CreditDetail.order_detail_id)
        )
        return {row.order_detail_id: row.total for row in result.fetchall()}

    async def _recalculate_detail_statuses(self, order: Order) -> None:
        order_detail_ids = [d.id for d in order.details if d.id is not None]

        invoiced_totals = await self._get_invoiced_totals_for_order(order_detail_ids)
        credited_totals = await self._get_credited_totals_for_order(order_detail_ids)

        for detail in order.details:
            invoiced = invoiced_totals.get(detail.id, Decimal("0"))
            credited = credited_totals.get(detail.id, Decimal("0"))
            net_invoiced = invoiced - credited

            detail.shipping_balance = detail.total - net_invoiced
            detail.status = self._calculate_detail_status(
                detail.shipping_balance, detail.total
            )

    def _calculate_detail_status(
        self, shipping_balance: Decimal, order_total: Decimal
    ) -> OrderStatus:
        if shipping_balance < Decimal("0"):
            return OrderStatus.OVER_SHIPPED
        if shipping_balance.quantize(Decimal("0.01")) <= Decimal("0.01"):
            return OrderStatus.SHIPPED_COMPLETE
        if shipping_balance == order_total:
            return OrderStatus.OPEN
        return OrderStatus.PARTIAL_SHIPPED

    def _update_order_status(self, order: Order) -> None:
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
