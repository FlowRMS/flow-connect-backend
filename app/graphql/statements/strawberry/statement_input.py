from datetime import date
from uuid import UUID

import strawberry
from commons.db.v6.commission.statements import CommissionStatement
from commons.db.v6.common.creation_type import CreationType

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.statements.strawberry.statement_detail_input import (
    StatementDetailInput,
)


@strawberry.input
class StatementInput(BaseInputGQL[CommissionStatement]):
    statement_number: str
    entity_date: date
    factory_id: UUID
    details: list[StatementDetailInput]

    id: UUID | None = strawberry.UNSET
    creation_type: CreationType = strawberry.UNSET

    def to_orm_model(self) -> CommissionStatement:
        creation_type = (
            self.creation_type
            if self.creation_type != strawberry.UNSET
            else CreationType.MANUAL
        )
        statement = CommissionStatement(
            statement_number=self.statement_number,
            factory_id=self.factory_id,
            entity_date=self.entity_date,
            creation_type=creation_type,
            details=[detail.to_orm_model() for detail in self.details],
        )
        return statement
