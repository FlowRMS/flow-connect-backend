from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.invoices.services.invoice_service import InvoiceService
from app.graphql.invoices.strawberry.invoice_response import (
    InvoiceLiteResponse,
    InvoiceResponse,
)


@strawberry.type
class InvoicesQueries:
    @strawberry.field
    @inject
    async def invoice(
        self,
        service: Injected[InvoiceService],
        id: UUID,
    ) -> InvoiceResponse:
        invoice = await service.find_invoice_by_id(id)
        return InvoiceResponse.from_orm_model(invoice)

    @strawberry.field
    @inject
    async def invoice_search(
        self,
        service: Injected[InvoiceService],
        search_term: str,
        limit: int = 20,
        open_only: bool = False,
        unlocked_only: bool = False,
    ) -> list[InvoiceLiteResponse]:
        return InvoiceLiteResponse.from_orm_model_list(
            await service.search_invoices(
                search_term, limit, open_only=open_only, unlocked_only=unlocked_only
            )
        )
