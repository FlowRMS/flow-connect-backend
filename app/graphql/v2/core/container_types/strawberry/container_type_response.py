"""Strawberry response types for container types."""

from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry

from commons.db.v6 import ContainerType

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class ContainerTypeResponse(DTOMixin[ContainerType]):
    """Response type for container types."""

    _instance: strawberry.Private[ContainerType]
    id: UUID
    name: str
    length: Decimal  # in inches
    width: Decimal  # in inches
    height: Decimal  # in inches
    weight: Decimal  # tare weight in lbs
    position: int  # display position
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: ContainerType) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            name=model.name,
            length=model.length,
            width=model.width,
            height=model.height,
            weight=model.weight,
            position=model.position,
            created_at=model.created_at,
        )
