from datetime import date
from uuid import UUID

import strawberry
from commons.db.v6.commission import Invoice
from commons.db.v6.commission.invoices.invoice import InvoiceStatus
from commons.db.v6.common.creation_type import CreationType

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.invoices.strawberry.invoice_detail_input import InvoiceDetailInput


@strawberry.input
class InvoiceInput(BaseInputGQL[Invoice]):
    invoice_number: str
    entity_date: date
    order_id: UUID
    details: list[InvoiceDetailInput]

    id: UUID | None = strawberry.UNSET
    due_date: date | None = strawberry.UNSET
    published: bool = strawberry.UNSET
    locked: bool = strawberry.UNSET
    creation_type: CreationType = strawberry.UNSET
    status: InvoiceStatus = strawberry.UNSET

    def to_orm_model(self) -> Invoice:
        published = self.published if self.published != strawberry.UNSET else False
        locked = self.locked if self.locked != strawberry.UNSET else False
        creation_type = (
            self.creation_type
            if self.creation_type != strawberry.UNSET
            else CreationType.MANUAL
        )
        status = self.status if self.status != strawberry.UNSET else InvoiceStatus.OPEN

        invoice = Invoice(
            invoice_number=self.invoice_number,
            entity_date=self.entity_date,
            order_id=self.order_id,
            due_date=self.optional_field(self.due_date),
            published=published,
            locked=locked,
            creation_type=creation_type,
            details=[detail.to_orm_model() for detail in self.details],
        )
        invoice.status = status
        return invoice
