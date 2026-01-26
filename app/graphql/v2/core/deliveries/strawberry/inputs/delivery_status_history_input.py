from datetime import datetime, timezone
from uuid import UUID

import strawberry
from commons.db.v6 import DeliveryStatusHistory
from commons.db.v6.warehouse.deliveries.delivery_enums import DeliveryStatus

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class DeliveryStatusHistoryInput(BaseInputGQL[DeliveryStatusHistory]):
    """Input type for creating delivery status history entries."""

    delivery_id: UUID
    status: DeliveryStatus
    timestamp: datetime | None = None
    user_id: UUID | None = None
    note: str | None = None

    def to_orm_model(self) -> DeliveryStatusHistory:
        return DeliveryStatusHistory(
            delivery_id=self.delivery_id,
            status=self.status,
            timestamp=self.timestamp or datetime.now(timezone.utc),
            user_id=self.user_id,
            note=self.note,
        )
