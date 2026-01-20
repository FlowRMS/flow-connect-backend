from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.fulfillment import FulfillmentActivity, FulfillmentActivityType

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class FulfillmentActivityResponse(DTOMixin[FulfillmentActivity]):
    _instance: strawberry.Private[FulfillmentActivity]
    id: UUID
    activity_type: FulfillmentActivityType
    content: str | None
    metadata: strawberry.scalars.JSON | None
    created_at: datetime
    created_by_id: UUID

    @classmethod
    def from_orm_model(cls, model: FulfillmentActivity) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            activity_type=model.activity_type,
            content=model.content,
            metadata=model.metadata,
            created_at=model.created_at,
            created_by_id=model.created_by_id,
        )
