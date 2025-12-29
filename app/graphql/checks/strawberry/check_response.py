"""GraphQL response type for Check."""

from datetime import date
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission import Check

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class CheckResponse(DTOMixin[Check]):
    id: UUID
    # created_at: datetime
    check_number: str
    entity_date: date
    post_date: date | None
    commission_month: date | None
    commission: Decimal
    factory_id: UUID
    status: int
    creation_type: int

    @classmethod
    def from_orm_model(cls, model: Check) -> Self:
        return cls(
            id=model.id,
            # created_at=model.created_at,
            check_number=model.check_number,
            entity_date=model.entity_date,
            post_date=model.post_date,
            commission_month=model.commission_month,
            commission=model.commission,
            factory_id=model.factory_id,
            status=model.status,
            creation_type=model.creation_type,
        )

    @strawberry.field
    def url(self) -> str:
        return f"/cm/commissions/list{self.id}"
