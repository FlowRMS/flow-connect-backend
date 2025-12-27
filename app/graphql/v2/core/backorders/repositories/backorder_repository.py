from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.v2.core.backorders.strawberry.backorder_response import (
    BackorderResponse,
)
from commons.db.models.commission.invoice_detail import InvoiceDetail
from commons.db.models.commission.order import Order
from commons.db.models.commission.order_detail import OrderDetail
from commons.db.models.status_enums import OrderStatusEnum


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
        warehouse_id: UUID | None = None, # Not directly linked to Order?
        customer_id: UUID | None = None,
        product_id: UUID | None = None, # String or UUID? Commons uses UUID for products.
        limit: int = 100,
        offset: int = 0,
    ) -> list[BackorderResponse]:
        
        # Calculate shipped quantity per order detail
        shipped_subquery = (
            select(
                InvoiceDetail.order_detail_id,
                func.sum(InvoiceDetail.quantity).label("shipped_qty")
            )
            .group_by(InvoiceDetail.order_detail_id)
            .subquery()
        )

        stmt = (
            select(
                OrderDetail, 
                Order,
                func.coalesce(shipped_subquery.c.shipped_qty, 0).label("shipped_qty")
            )
            .join(Order, OrderDetail.order_id == Order.id)
            .outerjoin(shipped_subquery, OrderDetail.id == shipped_subquery.c.order_detail_id)
            .where(
                Order.status.in_([OrderStatusEnum.OPEN, OrderStatusEnum.PARTIAL_SHIPPED])
            )
        )

        # Filter logic
        if customer_id:
            stmt = stmt.where(Order.sold_to_customer_id == customer_id)
        
        if product_id:
            stmt = stmt.where(OrderDetail.product_id == product_id)

        # Filter where ordered > shipped
        # Note: OrderDetail.quantity is int, InvoiceDetail.quantity is Decimal. Cast might be needed.
        stmt = stmt.where(OrderDetail.quantity > func.coalesce(shipped_subquery.c.shipped_qty, 0))

        stmt = stmt.limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        rows = result.all()
        
        response = []
        for row in rows:
            order_detail: OrderDetail = row[0]
            order: Order = row[1]
            shipped_qty = float(row[2])
            
            backordered_qty = float(order_detail.quantity) - shipped_qty
            
            response.append(BackorderResponse(
                order_id=order.id,
                order_number=order.order_number,
                product_id=str(order_detail.product_id),
                customer_id=order.sold_to_customer_id,
                ordered_quantity=order_detail.quantity,
                shipped_quantity=shipped_qty,
                backordered_quantity=backordered_qty,
                due_date=order.due_date,
                status=OrderStatusEnum(order.status).name if order.status is not None else "UNKNOWN"
            ))
            
        return response
