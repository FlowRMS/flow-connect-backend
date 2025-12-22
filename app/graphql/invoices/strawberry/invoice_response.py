"""GraphQL response type for Invoice."""

from datetime import date, datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission import Invoice

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class InvoiceResponse(DTOMixin[Invoice]):
    id: UUID
    entry_date: datetime
    invoice_number: str
    entity_date: date
    due_date: date | None
    factory_id: UUID | None
    order_id: UUID
    user_owner_ids: list[UUID]
    status: int
    published: bool
    locked: bool
    created_by: UUID
    creation_type: int
    balance_id: UUID

    @classmethod
    def from_orm_model(cls, model: Invoice) -> Self:
        return cls(
            id=model.id,
            entry_date=model.entry_date,
            invoice_number=model.invoice_number,
            entity_date=model.entity_date,
            due_date=model.due_date,
            factory_id=model.factory_id,
            order_id=model.order_id,
            user_owner_ids=model.user_owner_ids,
            status=model.status,
            published=model.published,
            locked=model.locked,
            created_by=model.created_by,
            creation_type=model.creation_type,
            balance_id=model.balance_id,
        )

    @strawberry.field
    def url(self) -> str:
        return f"/cm/invoices/list/{self.id}"
