from datetime import date
from uuid import UUID

import strawberry
from commons.db.v6.commission import Credit
from commons.db.v6.commission.credits.enums import CreditType
from commons.db.v6.common.creation_type import CreationType

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.credits.strawberry.credit_detail_input import CreditDetailInput


@strawberry.input
class CreditInput(BaseInputGQL[Credit]):
    credit_number: str
    entity_date: date
    order_id: UUID
    credit_type: CreditType
    details: list[CreditDetailInput]

    id: UUID | None = strawberry.UNSET
    reason: str | None = strawberry.UNSET
    creation_type: CreationType = strawberry.UNSET

    def to_orm_model(self) -> Credit:
        creation_type = (
            self.creation_type
            if self.creation_type != strawberry.UNSET
            else CreationType.MANUAL
        )
        credit_type = (
            self.credit_type
            if self.credit_type != strawberry.UNSET
            else CreditType.OTHER
        )

        credit = Credit(
            credit_number=self.credit_number,
            entity_date=self.entity_date,
            order_id=self.order_id,
            reason=self.optional_field(self.reason),
            locked=False,
            creation_type=creation_type,
            credit_type=credit_type,
            details=[detail.to_orm_model() for detail in self.details],
        )
        return credit
