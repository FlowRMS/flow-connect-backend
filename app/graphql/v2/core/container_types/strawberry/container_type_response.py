"""Strawberry response types for container types."""

from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.container_types.models import ContainerType


@strawberry.type
class ContainerTypeResponse(DTOMixin[ContainerType]):
    """Response type for container types."""

    _instance: strawberry.Private[ContainerType]
    id: UUID
    name: str
    length: float  # in inches
    width: float  # in inches
    height: float  # in inches
    weight: float  # tare weight in lbs
    order: int  # display order
    created_at: datetime | None

    @classmethod
    def from_orm_model(cls, model: ContainerType) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            name=model.name,
            length=float(model.length),
            width=float(model.width),
            height=float(model.height),
            weight=float(model.weight),
            order=model.order,
            created_at=model.created_at,
        )
