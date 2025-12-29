from decimal import Decimal
from uuid import UUID

from commons.db.v6.commission.invoices.invoice_detail import InvoiceDetail
from commons.db.v6.commission.orders.enums import OrderStatus
from commons.db.v6.commission.orders.order import Order
from commons.db.v6.commission.orders.order_detail import OrderDetail
from commons.db.v6.core.customers.customer import Customer
from commons.db.v6.core.products.product import Product
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.v2.core.backorders.strawberry.backorder_response import (
    BackorderResponse,
)
from app.graphql.v2.core.customers.strawberry.customer_response import (
    CustomerLiteResponse,
)
from app.graphql.v2.core.products.strawberry.product_response import ProductLiteResponse


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
        warehouse_id: UUID | None = None,  # Kept for compatibility, though currently unused in query
        customer_id: UUID | None = None,
        product_id: UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BackorderResponse]:
        # Calculate shipped quantity per order detail
        # Use Decimal for calculations involving money/quantities where precision matters, 
        # but here we cast at the end to match DTO if needed.
        shipped_subquery = (
            select(
                InvoiceDetail.order_detail_id,
                func.coalesce(func.sum(InvoiceDetail.quantity), 0).label("shipped_qty"),
            )
            .group_by(InvoiceDetail.order_detail_id)
            .subquery()
        )

        stmt = (
            select(
                OrderDetail,
                Order,
                func.coalesce(shipped_subquery.c.shipped_qty, 0).label("shipped_qty"),
                Product,
                Customer,
            )
            .join(Order, OrderDetail.order_id == Order.id)
            .outerjoin(Product, OrderDetail.product_id == Product.id)
            .outerjoin(Customer, Order.sold_to_customer_id == Customer.id)
            .outerjoin(
                shipped_subquery, OrderDetail.id == shipped_subquery.c.order_detail_id
            )
            .where(
                Order.status.in_(
                    [OrderStatus.OPEN, OrderStatus.PARTIAL_SHIPPED]
                )
            )
        )

        # Filter logic
        if customer_id:
            stmt = stmt.where(Order.sold_to_customer_id == customer_id)

        if product_id:
            stmt = stmt.where(OrderDetail.product_id == product_id)

        # Filter where ordered > shipped
        # Note: OrderDetail.quantity is usually Decimal/int in models, InvoiceDetail.quantity is Decimal.
        # We ensure strict comparison.
        stmt = stmt.where(
            OrderDetail.quantity > func.coalesce(shipped_subquery.c.shipped_qty, 0)
        )

        stmt = stmt.limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        rows = result.all()

        response = []
        for row in rows:
            order_detail: OrderDetail = row[0]
            order: Order = row[1]
            shipped_qty = Decimal(row[2]) if row[2] is not None else Decimal("0")
            product: Product | None = row[3]
            customer: Customer | None = row[4]

            # Ensure quantities are handled safely
            ordered_qty_val = order_detail.quantity or Decimal("0")
            backordered_qty = ordered_qty_val - shipped_qty

            response.append(
                BackorderResponse(
                    order_id=order.id,
                    order_number=order.order_number,
                    product_id=order_detail.product_id,
                    product=ProductLiteResponse.from_orm_model(product)
                    if product
                    else None,
                    customer_id=order.sold_to_customer_id,
                    customer=CustomerLiteResponse.from_orm_model(customer)
                    if customer
                    else None,
                    ordered_quantity=order_detail.quantity,
                    shipped_quantity=shipped_qty,
                    backordered_quantity=backordered_qty,
                    due_date=order.due_date,
                    status=OrderStatus(order.status).name
                    if order.status is not None
                    else "UNKNOWN",
                )
            )

        return response
