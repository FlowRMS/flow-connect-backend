from datetime import date
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm import Quote

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class QuoteResponse(DTOMixin[Quote]):
    id: UUID
    quote_number: str
    entity_date: date
    created_by_id: UUID
    sold_to_customer_id: UUID
    bill_to_customer_id: UUID | None
    exp_date: date | None
    blanket: bool

    @classmethod
    def from_orm_model(cls, model: Quote) -> Self:
        return cls(
            id=model.id,
            quote_number=model.quote_number,
            entity_date=model.entity_date,
            created_by_id=model.created_by_id,
            sold_to_customer_id=model.sold_to_customer_id,
            bill_to_customer_id=model.bill_to_customer_id,
            exp_date=model.exp_date,
            blanket=model.blanket,
        )

    @strawberry.field
    def url(self) -> str:
        return f"/crm/quotes/list/{self.id}"
