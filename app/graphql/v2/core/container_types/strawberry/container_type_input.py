"""Strawberry input types for container types."""

import strawberry

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.v2.core.container_types.models import ContainerType


@strawberry.input
class ContainerTypeInput(BaseInputGQL[ContainerType]):
    """Input type for creating/updating container types."""

    name: str
    length: float  # in inches
    width: float  # in inches
    height: float  # in inches
    weight: float  # tare weight in lbs
    order: int | None = None  # display order (auto-assigned if not provided)

    def to_orm_model(self) -> ContainerType:
        return ContainerType(
            name=self.name,
            length=self.length,  # type: ignore[arg-type]
            width=self.width,  # type: ignore[arg-type]
            height=self.height,  # type: ignore[arg-type]
            weight=self.weight,  # type: ignore[arg-type]
            order=self.order or 0,  # Will be auto-assigned if 0
        )
