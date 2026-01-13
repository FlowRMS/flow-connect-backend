from datetime import date
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.commission.orders.order_detail import OrderDetail

from app.core.db.adapters.dto import DTOMixin
from app.graphql.inject import inject
from app.graphql.v2.core.backorders.repositories.backorder_repository import (
    BackorderRepository,
)
from app.graphql.v2.core.customers.strawberry.customer_response import (
    CustomerLiteResponse,
)
from app.graphql.v2.core.products.strawberry.product_response import ProductLiteResponse


@strawberry.type
class BackorderResponse(DTOMixin[OrderDetail]):
    _instance: strawberry.Private[OrderDetail]

    # OrderDetail fields
    id: UUID
    ordered_quantity: Decimal

    # Computed/Related fields
    order_id: UUID
    order_number: str

    product_id: UUID | None
    product: ProductLiteResponse | None

    customer_id: UUID | None
    customer: CustomerLiteResponse | None

    due_date: date
    status: str

    @classmethod
    def from_orm_model(cls, model: OrderDetail) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            ordered_quantity=model.quantity,
            order_id=model.order_id,
            order_number=model.order.order_number,
            product_id=model.product_id,
            product=ProductLiteResponse.from_orm_model(model.product)
            if model.product
            else None,
            customer_id=model.order.sold_to_customer_id,
            customer=CustomerLiteResponse.from_orm_model(model.order.sold_to_customer)
            if model.order.sold_to_customer
            else None,
            due_date=model.order.due_date,
            status=model.order.status.name if model.order.status else "UNKNOWN",
        )

    @strawberry.field
    @inject
    async def shipped_quantity(self, repo: Injected[BackorderRepository]) -> Decimal:
        return await repo.get_shipped_qty(self.id)

    @strawberry.field
    @inject
    async def backordered_quantity(
        self, repo: Injected[BackorderRepository]
    ) -> Decimal:
        shipped = await repo.get_shipped_qty(self.id)
        return self.ordered_quantity - shipped
