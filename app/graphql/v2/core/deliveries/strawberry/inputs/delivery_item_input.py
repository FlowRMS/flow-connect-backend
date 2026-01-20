
from uuid import UUID

import strawberry
from commons.db.v6 import DeliveryItem
from commons.db.v6.warehouse.deliveries.delivery_enums import DeliveryItemStatus

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class DeliveryItemInput(BaseInputGQL[DeliveryItem]):
    """Input type for creating/updating delivery items."""

    delivery_id: UUID
    product_id: UUID
    expected_quantity: int = 0
    received_quantity: int = 0
    damaged_quantity: int = 0
    status: DeliveryItemStatus = DeliveryItemStatus.PENDING
    discrepancy_notes: str | None = None

    def to_orm_model(self) -> DeliveryItem:
        return DeliveryItem(
            delivery_id=self.delivery_id,
            product_id=self.product_id,
            expected_quantity=self.expected_quantity,
            received_quantity=self.received_quantity,
            damaged_quantity=self.damaged_quantity,
            status=self.status,
            discrepancy_notes=self.discrepancy_notes,
        )
