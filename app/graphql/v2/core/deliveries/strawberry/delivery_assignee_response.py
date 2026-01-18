
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import DeliveryAssignee, WarehouseMemberRole

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class DeliveryAssigneeResponse(DTOMixin[DeliveryAssignee]):
    """Response type for delivery assignees."""

    _instance: strawberry.Private[DeliveryAssignee]
    id: UUID
    delivery_id: UUID
    user_id: UUID
    role: WarehouseMemberRole

    @classmethod
    def from_orm_model(cls, model: DeliveryAssignee) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            delivery_id=model.delivery_id,
            user_id=model.user_id,
            role=model.role,
        )
