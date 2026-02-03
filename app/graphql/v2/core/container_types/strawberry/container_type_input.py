from decimal import Decimal

import strawberry
from commons.db.v6 import ContainerType

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class ContainerTypeInput(BaseInputGQL[ContainerType]):
    """Input type for creating/updating container types."""

    name: str
    length: Decimal  # in inches
    width: Decimal  # in inches
    height: Decimal  # in inches
    weight: Decimal  # tare weight in lbs
    position: int | None = None  # display position (auto-assigned if not provided)

    def to_orm_model(self) -> ContainerType:
        return ContainerType(
            name=self.name,
            length=self.length,
            width=self.width,
            height=self.height,
            weight=self.weight,
            position=self.position or 0,  # Will be auto-assigned if 0
        )
