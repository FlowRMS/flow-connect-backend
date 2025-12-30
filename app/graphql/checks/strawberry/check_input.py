from datetime import date
from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.commission import Check
from commons.db.v6.commission.checks.enums import CheckStatus
from commons.db.v6.common.creation_type import CreationType

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.checks.strawberry.check_detail_input import CheckDetailInput


@strawberry.input
class CheckInput(BaseInputGQL[Check]):
    check_number: str
    entity_date: date
    factory_id: UUID
    entered_commission_amount: Decimal
    details: list[CheckDetailInput]

    id: UUID | None = strawberry.UNSET
    post_date: date | None = strawberry.UNSET
    commission_month: date | None = strawberry.UNSET
    status: CheckStatus = strawberry.UNSET
    creation_type: CreationType = strawberry.UNSET

    def to_orm_model(self) -> Check:
        status = self.status if self.status != strawberry.UNSET else CheckStatus.OPEN
        creation_type = (
            self.creation_type
            if self.creation_type != strawberry.UNSET
            else CreationType.MANUAL
        )

        check = Check(
            check_number=self.check_number,
            entity_date=self.entity_date,
            factory_id=self.factory_id,
            entered_commission_amount=self.entered_commission_amount,
            post_date=self.optional_field(self.post_date),
            commission_month=self.optional_field(self.commission_month),
            status=status,
            creation_type=creation_type,
            details=[detail.to_orm_model() for detail in self.details],
        )
        return check
