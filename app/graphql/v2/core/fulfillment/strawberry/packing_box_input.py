from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.fulfillment import PackingBox

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class CreatePackingBoxInput(BaseInputGQL[PackingBox]):
    container_type_id: UUID | None = None
    length: Decimal | None = None
    width: Decimal | None = None
    height: Decimal | None = None
    weight: Decimal | None = None

    def to_orm_model(self) -> PackingBox:
        box = PackingBox(
            length=self.length,
            width=self.width,
            height=self.height,
            weight=self.weight,
        )
        box.container_type_id = self.container_type_id
        box.box_number = 0  # Will be set by service
        return box


@strawberry.input
class UpdatePackingBoxInput(BaseInputGQL[PackingBox]):
    container_type_id: UUID | None = strawberry.UNSET
    length: Decimal | None = strawberry.UNSET
    width: Decimal | None = strawberry.UNSET
    height: Decimal | None = strawberry.UNSET
    weight: Decimal | None = strawberry.UNSET
    tracking_number: str | None = strawberry.UNSET


@strawberry.input
class AssignItemToBoxInput:
    box_id: UUID
    line_item_id: UUID
    quantity: Decimal
