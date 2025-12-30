from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.commission import Deduction
from commons.db.v6.common.creation_type import CreationType

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.deductions.strawberry.deduction_split_rate_input import (
    DeductionSplitRateInput,
)


@strawberry.input
class DeductionInput(BaseInputGQL[Deduction]):
    check_id: UUID
    factory_id: UUID
    amount: Decimal
    split_rates: list[DeductionSplitRateInput]

    id: UUID | None = strawberry.UNSET
    reason: str | None = strawberry.UNSET
    creation_type: CreationType = strawberry.UNSET

    def to_orm_model(self) -> Deduction:
        creation_type = (
            self.creation_type
            if self.creation_type != strawberry.UNSET
            else CreationType.MANUAL
        )

        deduction = Deduction(
            check_id=self.check_id,
            factory_id=self.factory_id,
            amount=self.amount,
            reason=self.optional_field(self.reason),
            creation_type=creation_type,
            split_rates=[sr.to_orm_model() for sr in self.split_rates],
        )
        return deduction
