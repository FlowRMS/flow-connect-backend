from datetime import date
from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.invoices.services.invoice_service import InvoiceService
from app.graphql.invoices.strawberry.invoice_input import InvoiceInput
from app.graphql.invoices.strawberry.invoice_response import InvoiceResponse
from app.graphql.invoices.strawberry.order_detail_to_invoice_input import (
    OrderDetailToInvoiceDetailInput,
)


@strawberry.type
class InvoicesMutations:
    @strawberry.mutation
    @inject
    async def create_invoice(
        self,
        input: InvoiceInput,
        service: Injected[InvoiceService],
    ) -> InvoiceResponse:
        invoice = await service.create_invoice(invoice_input=input)
        return InvoiceResponse.from_orm_model(invoice)

    @strawberry.mutation
    @inject
    async def update_invoice(
        self,
        input: InvoiceInput,
        service: Injected[InvoiceService],
    ) -> InvoiceResponse:
        invoice = await service.update_invoice(invoice_input=input)
        return InvoiceResponse.from_orm_model(invoice)

    @strawberry.mutation
    @inject
    async def delete_invoice(
        self,
        id: UUID,
        service: Injected[InvoiceService],
    ) -> bool:
        return await service.delete_invoice(invoice_id=id)

    @strawberry.mutation
    @inject
    async def create_invoice_from_order(
        self,
        order_id: UUID,
        invoice_number: str,
        factory_id: UUID,
        service: Injected[InvoiceService],
        order_details_inputs: list[OrderDetailToInvoiceDetailInput] | None = None,
        due_date: date | None = None,
    ) -> InvoiceResponse:
        invoice = await service.create_invoice_from_order(
            order_id=order_id,
            invoice_number=invoice_number,
            factory_id=factory_id,
            order_details_inputs=order_details_inputs,
            due_date=due_date,
        )
        return InvoiceResponse.from_orm_model(invoice)
