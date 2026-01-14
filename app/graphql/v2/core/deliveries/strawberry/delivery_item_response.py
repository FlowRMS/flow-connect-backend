
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import DeliveryItem

from app.core.db.adapters.dto import DTOMixin

from .delivery_enums import DeliveryItemStatusGQL
from .delivery_issue_response import DeliveryIssueResponse
from .delivery_item_receipt_response import DeliveryItemReceiptResponse
from app.graphql.v2.core.products.strawberry.product_response import (
    ProductLiteResponse,
)


@strawberry.type
class DeliveryItemResponse(DTOMixin[DeliveryItem]):
    """Response type for delivery items."""

    _instance: strawberry.Private[DeliveryItem]
    id: UUID
    delivery_id: UUID
    product_id: UUID
    expected_qty: int
    received_qty: int
    damaged_qty: int
    status: DeliveryItemStatusGQL
    discrepancy_notes: str | None

    @classmethod
    def from_orm_model(cls, model: DeliveryItem) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            delivery_id=model.delivery_id,
            product_id=model.product_id,
            expected_qty=model.expected_quantity,
            received_qty=model.received_quantity,
            damaged_qty=model.damaged_quantity,
            status=DeliveryItemStatusGQL(model.status.value),
            discrepancy_notes=model.discrepancy_notes,
        )

    @strawberry.field
    async def receipts(self) -> list[DeliveryItemReceiptResponse]:
        receipts = await self._instance.awaitable_attrs.receipts
        return DeliveryItemReceiptResponse.from_orm_model_list(receipts)

    @strawberry.field
    async def issues(self) -> list[DeliveryIssueResponse]:
        issues = await self._instance.awaitable_attrs.issues
        return DeliveryIssueResponse.from_orm_model_list(issues)

    @strawberry.field
    async def product(self) -> ProductLiteResponse:
        product = await self._instance.awaitable_attrs.product
        return ProductLiteResponse.from_orm_model(product)
