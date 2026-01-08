from decimal import Decimal
from uuid import UUID

from commons.db.v6.commission.invoices.invoice_detail import InvoiceDetail
from commons.db.v6.commission.orders.enums import OrderStatus
from commons.db.v6.commission.orders.order import Order
from commons.db.v6.commission.orders.order_detail import OrderDetail
from commons.db.v6.warehouse.inventory.inventory import Inventory
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


from app.core.constants import DEFAULT_QUERY_LIMIT, DEFAULT_QUERY_OFFSET

class BackorderRepository(BaseRepository[OrderDetail]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            OrderDetail,
        )

    async def get_backorders(
        self,
        customer_id: UUID | None = None,
        product_id: UUID | None = None,
        limit: int = DEFAULT_QUERY_LIMIT,
        offset: int = DEFAULT_QUERY_OFFSET,
    ) -> list[OrderDetail]:
        """
        Retrieve backordered order details with calculated availability.

        Backorders are identified where:
        1. Order status is OPEN or PARTIAL_SHIPPED
        2. Ordered quantity > Shipped quantity
        3. Remaining needed quantity > Total available inventory for the product

        The query calculates:
        - Shipped quantity from invoice details
        - Total available inventory across all warehouses
        """
        # Subquery to calculate shipped quantity
        shipped_subquery = (
            select(
                InvoiceDetail.order_detail_id,
                func.coalesce(func.sum(InvoiceDetail.quantity), 0).label("shipped_qty"),
            )
            .group_by(InvoiceDetail.order_detail_id)
            .subquery()
        )

        # Subquery for total available inventory per product (across all warehouses)
        inventory_subquery = (
            select(
                Inventory.product_id,
                func.coalesce(func.sum(Inventory.available_quantity), 0).label(
                    "total_available"
                ),
            )
            .group_by(Inventory.product_id)
            .subquery()
        )

        stmt = (
            select(OrderDetail)
            .options(
                selectinload(OrderDetail.order).selectinload(Order.sold_to_customer),
                selectinload(OrderDetail.product),
            )
            .join(Order, OrderDetail.order_id == Order.id)
            .outerjoin(
                shipped_subquery, OrderDetail.id == shipped_subquery.c.order_detail_id
            )
            .outerjoin(
                inventory_subquery,
                OrderDetail.product_id == inventory_subquery.c.product_id,
            )
            .where(
                Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL_SHIPPED])
            )
        )

        if customer_id:
            stmt = stmt.where(Order.sold_to_customer_id == customer_id)

        if product_id:
            stmt = stmt.where(OrderDetail.product_id == product_id)

        # Filter where ordered > shipped
        stmt = stmt.where(
            OrderDetail.quantity > func.coalesce(shipped_subquery.c.shipped_qty, 0)
        )

        # Filter where needed quantity > available inventory (true backorder)
        stmt = stmt.where(
            (OrderDetail.quantity - func.coalesce(shipped_subquery.c.shipped_qty, 0))
            > func.coalesce(inventory_subquery.c.total_available, 0)
        )

        stmt = stmt.limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_shipped_qty(self, order_detail_id: UUID) -> Decimal:
        stmt = select(func.sum(InvoiceDetail.quantity)).where(
            InvoiceDetail.order_detail_id == order_detail_id
        )
        result = await self.session.execute(stmt)
        return result.scalar() or Decimal("0")
