
from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import DeliveryIssue

from app.core.db.adapters.dto import DTOMixin

from .delivery_enums import DeliveryIssueStatusGQL, DeliveryIssueTypeGQL


@strawberry.type
class DeliveryIssueResponse(DTOMixin[DeliveryIssue]):
    """Response type for delivery issues."""

    _instance: strawberry.Private[DeliveryIssue]
    id: UUID
    delivery_id: UUID
    delivery_item_id: UUID
    receipt_id: UUID | None
    issue_type: DeliveryIssueTypeGQL
    custom_issue_type: str | None
    quantity: int
    status: DeliveryIssueStatusGQL
    description: str | None
    notes: str | None
    communicated_at: datetime | None
    created_at: datetime
    created_by_id: UUID | None

    @classmethod
    def from_orm_model(cls, model: DeliveryIssue) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            delivery_id=model.delivery_id,
            delivery_item_id=model.delivery_item_id,
            receipt_id=model.receipt_id,
            issue_type=DeliveryIssueTypeGQL(model.issue_type.value),
            custom_issue_type=model.custom_issue_type,
            quantity=model.quantity,
            status=DeliveryIssueStatusGQL(model.status.value),
            description=model.description,
            notes=model.notes,
            communicated_at=model.communicated_at,
            created_at=model.created_at,
            created_by_id=model.created_by_id,
        )
