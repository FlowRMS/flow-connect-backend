from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.warehouse.shipment_requests.shipment_request_item import (
    ShipmentRequestItem,
)

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.products.strawberry.product_response import (
    ProductLiteResponse,
)


@strawberry.type
class ShipmentRequestItemResponse(DTOMixin[ShipmentRequestItem]):
    _instance: strawberry.Private[ShipmentRequestItem]
    id: UUID
    request_id: UUID
    product_id: UUID
    quantity: Decimal
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: ShipmentRequestItem) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            request_id=model.request_id,
            product_id=model.product_id,
            quantity=model.quantity,
            created_at=model.created_at,
        )

    @strawberry.field
    async def product(self) -> ProductLiteResponse:
        from app.graphql.v2.core.products.strawberry.product_response import (
            ProductLiteResponse,
        )

        product = await self._instance.awaitable_attrs.product
        return ProductLiteResponse.from_orm_model(product)
