from datetime import date
from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.commission.orders import OrderAcknowledgement
from commons.db.v6.common.creation_type import CreationType

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class OrderAcknowledgementInput(BaseInputGQL[OrderAcknowledgement]):
    order_id: UUID
    order_detail_id: UUID
    order_acknowledgement_number: str
    entity_date: date
    quantity: Decimal

    id: UUID | None = strawberry.UNSET
    ship_date: date | None = strawberry.UNSET
    creation_type: CreationType = strawberry.UNSET

    def to_orm_model(self) -> OrderAcknowledgement:
        creation_type = (
            self.creation_type
            if self.creation_type != strawberry.UNSET
            else CreationType.MANUAL
        )

        return OrderAcknowledgement(
            order_id=self.order_id,
            order_detail_id=self.order_detail_id,
            order_acknowledgement_number=self.order_acknowledgement_number,
            entity_date=self.entity_date,
            quantity=self.quantity,
            ship_date=self.optional_field(self.ship_date),
            creation_type=creation_type,
        )
