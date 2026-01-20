
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import DeliveryItem
from commons.db.v6.warehouse.deliveries.delivery_enums import DeliveryItemStatus

from app.core.db.adapters.dto import DTOMixin

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
    expected_quantity: int
    received_quantity: int
    damaged_quantity: int
    status: DeliveryItemStatus
    discrepancy_notes: str | None

    @classmethod
    def from_orm_model(cls, model: DeliveryItem) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            delivery_id=model.delivery_id,
            product_id=model.product_id,
            expected_quantity=model.expected_quantity,
            received_quantity=model.received_quantity,
            damaged_quantity=model.damaged_quantity,
            status=model.status,
            discrepancy_notes=model.discrepancy_notes,
        )

    @strawberry.field
    def receipts(self) -> list[DeliveryItemReceiptResponse]:
        """Receipts - pre-loaded via repository."""
        return DeliveryItemReceiptResponse.from_orm_model_list(self._instance.receipts)

    @strawberry.field
    def issues(self) -> list[DeliveryIssueResponse]:
        """Issues - pre-loaded via repository."""
        return DeliveryIssueResponse.from_orm_model_list(self._instance.issues)

    @strawberry.field
    def product(self) -> ProductLiteResponse:
        """Product - pre-loaded via repository."""
        return ProductLiteResponse.from_orm_model(self._instance.product)
