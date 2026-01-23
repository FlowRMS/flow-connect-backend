from datetime import datetime
from uuid import UUID

import strawberry
from commons.db.v6 import DeliveryItemReceipt
from commons.db.v6.warehouse.deliveries.delivery_enums import DeliveryReceiptType

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class DeliveryItemReceiptInput(BaseInputGQL[DeliveryItemReceipt]):
    """Input type for creating/updating delivery item receipts."""

    delivery_item_id: UUID
    receipt_type: DeliveryReceiptType = DeliveryReceiptType.RECEIPT
    received_quantity: int = 0
    damaged_quantity: int = 0
    location_id: UUID | None = None
    received_by_id: UUID | None = None
    received_at: datetime | None = None
    note: str | None = None

    def to_orm_model(self) -> DeliveryItemReceipt:
        return DeliveryItemReceipt(
            delivery_item_id=self.delivery_item_id,
            receipt_type=self.receipt_type,
            received_quantity=self.received_quantity,
            damaged_quantity=self.damaged_quantity,
            location_id=self.location_id,
            received_by_id=self.received_by_id,
            received_at=self.received_at,
            note=self.note,
        )
