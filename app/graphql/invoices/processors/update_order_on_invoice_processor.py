from decimal import Decimal
from uuid import UUID

from commons.db.v6.commission import Invoice, InvoiceDetail, OrderDetail
from commons.db.v6.commission.orders import Order, OrderHeaderStatus, OrderStatus
from loguru import logger
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
        return [
            RepositoryEvent.POST_CREATE,
            RepositoryEvent.POST_UPDATE,
            RepositoryEvent.POST_DELETE,
        ]

    async def process(self, context: EntityContext[Invoice]) -> None:
        logger.info(
            f"Processing UpdateOrderOnInvoiceProcessor for Invoice {context.entity.id} on event {context.event.name}"
        )
        invoice = context.entity

        order = await self._get_order_with_details(invoice.order_id)
        if order is None:
            return

        await self._update_order_detail_statuses(order, invoice, context.event)
        self._update_order_status(order)
        await self.session.flush()

    async def _get_order_with_details(self, order_id: UUID) -> Order | None:
        result = await self.session.execute(
            select(Order).options(joinedload(Order.details)).where(Order.id == order_id)
        )
        return result.unique().scalar_one_or_none()

    async def get_order_detail_totals(self, order_id: UUID) -> dict[UUID, Decimal]:
        result = await self.session.execute(
            select(
                OrderDetail.id.label("order_detail_id"),
                func.coalesce(func.sum(InvoiceDetail.total), Decimal("0")).label(
                    "total"
                ),
            )
            .select_from(OrderDetail)
            .outerjoin(InvoiceDetail, InvoiceDetail.order_detail_id == OrderDetail.id)
            .where(OrderDetail.order_id == order_id)
            .group_by(OrderDetail.id)
        )
        return {row.order_detail_id: row.total for row in result.fetchall()}

    async def _update_order_detail_statuses(
        self, order: Order, invoice: Invoice, event: RepositoryEvent
    ) -> None:
        order_detail_mapping = {detail.id: detail for detail in order.details}
        invoice_detail_totals = await self.get_order_detail_totals(order.id)
        logger.info(
            f"Updating Order {order.id} details based on Invoice {invoice.id} event {event.name}"
        )
        logger.info(f"Invoice Detail Totals: {invoice_detail_totals}")

        for order_detail_id, invoiced_amount in invoice_detail_totals.items():
            order_detail = order_detail_mapping.get(order_detail_id)

            if order_detail is None:
                continue

            logger.info(
                f"Updating OrderDetail {order_detail.id} with current balance {order_detail.shipping_balance} for Order {order.id} based on Invoice {invoice.id} event {event.name} with invoiced amount {invoiced_amount}"
            )
            if event == RepositoryEvent.POST_DELETE:
                order_detail.shipping_balance = order_detail.total + invoiced_amount
            else:
                order_detail.shipping_balance = order_detail.total - invoiced_amount

            order_detail.status = self._calculate_detail_status(
                order_detail.shipping_balance, order_detail.total
            )

    def _calculate_detail_status(
        self, shipping_balance: Decimal, order_total: Decimal
    ) -> OrderStatus:
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
