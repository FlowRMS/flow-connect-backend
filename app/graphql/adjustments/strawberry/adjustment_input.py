from datetime import date
from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.commission import Adjustment
from commons.db.v6.commission.checks.enums import AdjustmentAllocationMethod
from commons.db.v6.common.creation_type import CreationType

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.adjustments.strawberry.adjustment_split_rate_input import (
    AdjustmentSplitRateInput,
)


@strawberry.input
class AdjustmentInput(BaseInputGQL[Adjustment]):
    adjustment_number: str
    entity_date: date
    factory_id: UUID
    amount: Decimal
    allocation_method: AdjustmentAllocationMethod
    split_rates: list[AdjustmentSplitRateInput]

    id: UUID | None = strawberry.UNSET
    customer_id: UUID | None = strawberry.UNSET
    reason: str | None = strawberry.UNSET
    creation_type: CreationType = strawberry.UNSET

    def to_orm_model(self) -> Adjustment:
        creation_type = (
            self.creation_type
            if self.creation_type != strawberry.UNSET
            else CreationType.MANUAL
        )

        adjustment = Adjustment(
            adjustment_number=self.adjustment_number,
            entity_date=self.entity_date,
            factory_id=self.factory_id,
            allocation_method=self.allocation_method,
            amount=self.amount,
            customer_id=self.optional_field(self.customer_id),
            reason=self.optional_field(self.reason),
            creation_type=creation_type,
            split_rates=[sr.to_orm_model() for sr in self.split_rates],
        )
        return adjustment
