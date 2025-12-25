from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.core.products.product_cpn import ProductCpn

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.customers.strawberry.customer_response import (
    CustomerLiteResponse,
)
from app.graphql.v2.core.products.strawberry.product_response import ProductLiteResponse


@strawberry.type
class ProductCpnResponse(DTOMixin[ProductCpn]):
    _instance: strawberry.Private[ProductCpn]
    id: UUID
    product_id: UUID
    customer_id: UUID
    customer_part_number: str
    unit_price: Decimal
    commission_rate: Decimal

    @classmethod
    def from_orm_model(cls, model: ProductCpn) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            product_id=model.product_id,
            customer_id=model.customer_id,
            customer_part_number=model.customer_part_number,
            unit_price=model.unit_price,
            commission_rate=model.commission_rate,
        )

    @strawberry.field
    async def product(self) -> ProductLiteResponse:
        return ProductLiteResponse.from_orm_model(
            await self._instance.awaitable_attrs.product
        )

    @strawberry.field
    async def customer(self) -> CustomerLiteResponse:
        return CustomerLiteResponse.from_orm_model(
            await self._instance.awaitable_attrs.customer
        )
