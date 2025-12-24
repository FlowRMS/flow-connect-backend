"""GraphQL response type for Invoice."""

from datetime import date
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission import Invoice

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class InvoiceResponse(DTOMixin[Invoice]):
    id: UUID
    # created_at: datetime
    invoice_number: str
    entity_date: date
    due_date: date | None
    factory_id: UUID | None
    order_id: UUID
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
            # created_at=model.created_at,
            invoice_number=model.invoice_number,
            entity_date=model.entity_date,
            due_date=model.due_date,
            factory_id=model.factory_id,
            order_id=model.order_id,
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
