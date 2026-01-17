from datetime import date
from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.commission.orders import OrderAcknowledgement
from commons.db.v6.commission.orders.order_acknowledgement_detail import (
    OrderAcknowledgementDetail,
)
from commons.db.v6.common.creation_type import CreationType

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class OrderAcknowledgementDetailInput(BaseInputGQL[OrderAcknowledgementDetail]):
    order_detail_id: UUID
    id: UUID | None = strawberry.UNSET

    def to_orm_model(self) -> OrderAcknowledgementDetail:
        detail = OrderAcknowledgementDetail(
            order_detail_id=self.order_detail_id,
        )
        if self.id is not strawberry.UNSET and self.id is not None:
            detail.id = self.id
        return detail


@strawberry.input
class OrderAcknowledgementInput(BaseInputGQL[OrderAcknowledgement]):
    order_id: UUID
    details: list[OrderAcknowledgementDetailInput]
    order_acknowledgement_number: str
    entity_date: date
    quantity: Decimal

    id: UUID | None = strawberry.UNSET
    creation_type: CreationType = strawberry.UNSET

    def to_orm_model(self) -> OrderAcknowledgement:
        if not self.details:
            raise ValueError("At least one detail is required")

        creation_type = (
            self.creation_type
            if self.creation_type != strawberry.UNSET
            else CreationType.MANUAL
        )

        return OrderAcknowledgement(
            order_id=self.order_id,
            order_acknowledgement_number=self.order_acknowledgement_number,
            entity_date=self.entity_date,
            quantity=self.quantity,
            creation_type=creation_type,
            details=[detail.to_orm_model() for detail in self.details],
        )
