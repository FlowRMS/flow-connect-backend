from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.fulfillment import FulfillmentAssignment

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.fulfillment.strawberry.enums import FulfillmentAssignmentRole


@strawberry.type
class FulfillmentAssignmentResponse(DTOMixin[FulfillmentAssignment]):
    _instance: strawberry.Private[FulfillmentAssignment]
    id: UUID
    user_id: UUID
    role: FulfillmentAssignmentRole
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: FulfillmentAssignment) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            user_id=model.user_id,
            role=model.role,
            created_at=model.created_at,
        )

    @strawberry.field
    def user_name(self) -> str:
        """Get user name - relationship is eager-loaded."""
        return self._instance.user.full_name if self._instance.user else ""

    @strawberry.field
    def user_email(self) -> str:
        """Get user email - relationship is eager-loaded."""
        return self._instance.user.email if self._instance.user else ""
