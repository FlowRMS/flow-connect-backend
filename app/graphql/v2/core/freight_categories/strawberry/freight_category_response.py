from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.warehouse import FreightCategory

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class FreightCategoryResponse(DTOMixin[FreightCategory]):
    _instance: strawberry.Private[FreightCategory]
    id: UUID
    freight_class: Decimal
    description: str | None
    is_active: bool
    position: int
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: FreightCategory) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            freight_class=model.freight_class,
            description=model.description,
            is_active=model.is_active,
            position=model.position,
            created_at=model.created_at,
        )
