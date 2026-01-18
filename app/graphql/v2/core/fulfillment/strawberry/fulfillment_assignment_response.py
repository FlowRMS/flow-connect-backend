from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.fulfillment import FulfillmentAssignment, FulfillmentAssignmentRole

from app.core.db.adapters.dto import DTOMixin


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
    async def user_name(self) -> str:
        user = await self._instance.awaitable_attrs.user
        return user.full_name if user else ""

    @strawberry.field
    async def user_email(self) -> str:
        user = await self._instance.awaitable_attrs.user
        return user.email if user else ""
