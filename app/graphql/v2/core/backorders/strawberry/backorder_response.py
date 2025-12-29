from datetime import date
from decimal import Decimal
from uuid import UUID

import strawberry
from app.graphql.v2.core.customers.strawberry.customer_response import (
    CustomerLiteResponse,
)
from app.graphql.v2.core.products.strawberry.product_response import ProductLiteResponse


@strawberry.type
class BackorderResponse:
    order_id: UUID
    order_number: str
    product_id: UUID | None
    product: ProductLiteResponse | None

    customer_id: UUID | None
    customer: CustomerLiteResponse | None

    ordered_quantity: Decimal
    shipped_quantity: Decimal
    backordered_quantity: Decimal

    due_date: date
    status: str
