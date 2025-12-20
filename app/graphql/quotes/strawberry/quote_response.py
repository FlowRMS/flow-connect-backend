"""GraphQL response type for Quote."""

from datetime import date, datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.models import Quote

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class QuoteResponse(DTOMixin[Quote]):
    id: UUID
    entry_date: datetime
    quote_number: str
    entity_date: date
    created_by: UUID
    user_owner_ids: list[UUID]
    sold_to_customer_id: UUID | None
    bill_to_customer_id: UUID | None
    job_name: str | None
    exp_date: date | None
    blanket: bool

    @classmethod
    def from_orm_model(cls, model: Quote) -> Self:
        return cls(
            id=model.id,
            entry_date=model.entry_date,
            quote_number=model.quote_number,
            entity_date=model.entity_date,
            created_by=model.created_by,
            user_owner_ids=model.user_owner_ids,
            sold_to_customer_id=model.sold_to_customer_id,
            bill_to_customer_id=model.bill_to_customer_id,
            job_name=model.job_name,
            exp_date=model.exp_date,
            blanket=model.blanket,
        )

    @strawberry.field
    def url(self) -> str:
        return f"/crm/quotes/list/{self.id}"
