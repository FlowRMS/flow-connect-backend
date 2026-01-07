from decimal import Decimal
from uuid import UUID

from commons.db.v6.commission import Invoice, InvoiceDetail
from commons.db.v6.commission.orders import Order, OrderHeaderStatus, OrderStatus
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.processors import BaseProcessor, EntityContext, RepositoryEvent


class UpdateOrderOnInvoiceProcessor(BaseProcessor[Invoice]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.POST_CREATE, RepositoryEvent.POST_UPDATE]

    async def process(self, context: EntityContext[Invoice]) -> None:
        invoice = context.entity

        order = await self._get_order_with_details(invoice.order_id)
        if order is None:
            return

        await self._update_order_detail_statuses(order)
        self._update_order_status(order)
        await self.session.flush()

    async def _get_order_with_details(self, order_id: UUID) -> Order | None:
        result = await self.session.execute(
            select(Order).options(joinedload(Order.details)).where(Order.id == order_id)
        )
        return result.unique().scalar_one_or_none()

    async def _get_invoiced_amount_for_detail(self, order_detail_id: UUID) -> Decimal:
        result = await self.session.execute(
            select(func.coalesce(func.sum(InvoiceDetail.total), Decimal("0"))).where(
                InvoiceDetail.order_detail_id == order_detail_id
            )
        )
        return result.scalar_one()

    async def _update_order_detail_statuses(self, order: Order) -> None:
        for detail in order.details:
            invoiced_amount = await self._get_invoiced_amount_for_detail(detail.id)
            new_status = self._calculate_detail_status(detail.total, invoiced_amount)
            detail.status = new_status

    def _calculate_detail_status(
        self, order_total: Decimal, invoiced_total: Decimal
    ) -> OrderStatus:
        if invoiced_total <= Decimal("0"):
            return OrderStatus.OPEN
        if invoiced_total < order_total:
            return OrderStatus.PARTIAL_SHIPPED
        if invoiced_total == order_total:
            return OrderStatus.SHIPPED_COMPLETE
        return OrderStatus.OVER_SHIPPED

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
