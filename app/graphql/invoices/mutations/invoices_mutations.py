from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.invoices.services.invoice_service import InvoiceService
from app.graphql.invoices.strawberry.invoice_input import InvoiceInput
from app.graphql.invoices.strawberry.invoice_response import InvoiceResponse


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
