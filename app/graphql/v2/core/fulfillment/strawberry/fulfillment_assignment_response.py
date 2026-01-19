from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.fulfillment import FulfillmentAssignment

from app.core.db.adapters.dto import DTOMixin
from commons.db.v6.fulfillment.enums import FulfillmentAssignmentRole
from app.graphql.v2.core.users.strawberry import UserLiteResponse


@strawberry.type
class FulfillmentAssignmentResponse(DTOMixin[FulfillmentAssignment]):
    _instance: strawberry.Private[FulfillmentAssignment]
    id: UUID
    role: FulfillmentAssignmentRole
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: FulfillmentAssignment) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            role=model.role,
            created_at=model.created_at,
        )

    @strawberry.field
    def user(self) -> UserLiteResponse | None:
        """Get user - relationship is eager-loaded."""
        if self._instance.user:
            return UserLiteResponse.from_orm_model(self._instance.user)
        return None
