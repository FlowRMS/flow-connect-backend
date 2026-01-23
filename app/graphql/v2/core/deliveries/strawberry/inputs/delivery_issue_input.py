from datetime import datetime
from uuid import UUID

import strawberry
from commons.db.v6 import DeliveryIssue
from commons.db.v6.warehouse.deliveries.delivery_enums import (
    DeliveryIssueStatus,
    DeliveryIssueType,
)

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class DeliveryIssueInput(BaseInputGQL[DeliveryIssue]):
    """Input type for creating/updating delivery issues."""

    delivery_id: UUID
    delivery_item_id: UUID
    receipt_id: UUID | None = None
    issue_type: DeliveryIssueType
    custom_issue_type: str | None = None
    quantity: int = 0
    status: DeliveryIssueStatus = DeliveryIssueStatus.OPEN
    description: str | None = None
    notes: str | None = None
    communicated_at: datetime | None = None

    def to_orm_model(self) -> DeliveryIssue:
        return DeliveryIssue(
            delivery_id=self.delivery_id,
            delivery_item_id=self.delivery_item_id,
            receipt_id=self.receipt_id,
            issue_type=self.issue_type,
            custom_issue_type=self.custom_issue_type,
            quantity=self.quantity,
            status=self.status,
            description=self.description,
            notes=self.notes,
            communicated_at=self.communicated_at,
        )
