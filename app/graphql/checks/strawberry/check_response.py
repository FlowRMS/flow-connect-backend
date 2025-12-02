"""GraphQL response type for Check."""

from datetime import date, datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.models import Check

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class CheckResponse(DTOMixin[Check]):
    id: UUID
    entry_date: datetime
    check_number: str
    entity_date: date
    post_date: date | None
    commission_month: date | None
    commission: Decimal
    factory_id: UUID
    user_owner_ids: list[UUID]
    status: int
    created_by: UUID
    creation_type: int

    @classmethod
    def from_orm_model(cls, model: Check) -> Self:
        return cls(
            id=model.id,
            entry_date=model.entry_date,
            check_number=model.check_number,
            entity_date=model.entity_date,
            post_date=model.post_date,
            commission_month=model.commission_month,
            commission=model.commission,
            factory_id=model.factory_id,
            user_owner_ids=model.user_owner_ids,
            status=model.status,
            created_by=model.created_by,
            creation_type=model.creation_type,
        )
