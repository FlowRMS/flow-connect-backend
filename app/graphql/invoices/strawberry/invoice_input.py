from datetime import date
from uuid import UUID

import strawberry
from commons.db.v6.commission import Invoice
from commons.db.v6.common.creation_type import CreationType

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.invoices.strawberry.invoice_detail_input import InvoiceDetailInput


@strawberry.input
class InvoiceInput(BaseInputGQL[Invoice]):
    invoice_number: str
    entity_date: date
    order_id: UUID
    factory_id: UUID
    details: list[InvoiceDetailInput]

    id: UUID | None = strawberry.UNSET
    due_date: date | None = strawberry.UNSET
    creation_type: CreationType = strawberry.UNSET

    def to_orm_model(self) -> Invoice:
        creation_type = (
            self.creation_type
            if self.creation_type != strawberry.UNSET
            else CreationType.MANUAL
        )
        invoice = Invoice(
            invoice_number=self.invoice_number,
            factory_id=self.factory_id,
            entity_date=self.entity_date,
            order_id=self.order_id,
            due_date=self.optional_field(self.due_date),
            creation_type=creation_type,
            details=[detail.to_orm_model() for detail in self.details],
        )
        return invoice
