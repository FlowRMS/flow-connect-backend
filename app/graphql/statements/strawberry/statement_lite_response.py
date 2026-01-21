from datetime import date, datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission.statements import CommissionStatement
from commons.db.v6.common.creation_type import CreationType

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class StatementLiteResponse(DTOMixin[CommissionStatement]):
    _instance: strawberry.Private[CommissionStatement]
    id: UUID
    created_at: datetime
    created_by_id: UUID
    statement_number: str
    entity_date: date
    factory_id: UUID
    creation_type: CreationType
    balance_id: UUID

    @classmethod
    def from_orm_model(cls, model: CommissionStatement) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            created_at=model.created_at,
            created_by_id=model.created_by_id,
            statement_number=model.statement_number,
            entity_date=model.entity_date,
            factory_id=model.factory_id,
            creation_type=model.creation_type,
            balance_id=model.balance_id,
        )

    @strawberry.field
    def url(self) -> str:
        return f"/cm/statements/list/{self.id}"
