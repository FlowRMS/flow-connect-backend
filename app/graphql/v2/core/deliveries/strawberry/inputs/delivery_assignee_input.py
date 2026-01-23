from uuid import UUID

import strawberry
from commons.db.v6 import DeliveryAssignee, WarehouseMemberRole

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class DeliveryAssigneeInput(BaseInputGQL[DeliveryAssignee]):
    """Input type for assigning users to deliveries."""

    delivery_id: UUID
    user_id: UUID
    role: WarehouseMemberRole

    def to_orm_model(self) -> DeliveryAssignee:
        return DeliveryAssignee(
            delivery_id=self.delivery_id,
            user_id=self.user_id,
            role=self.role,
        )
