from typing import override
from uuid import UUID

from app.graphql.common.entity_source_type import EntitySourceType
from app.graphql.common.interfaces.entity_lookup_strategy import EntityLookupStrategy
from app.graphql.common.strawberry.entity_response import EntityResponse
from app.graphql.invoices.services.invoice_service import InvoiceService
from app.graphql.invoices.strawberry.invoice_response import InvoiceResponse


class InvoiceEntityStrategy(EntityLookupStrategy):
    def __init__(self, service: InvoiceService) -> None:
        super().__init__()
        self.service = service

    @override
    def get_supported_source_type(self) -> EntitySourceType:
        return EntitySourceType.INVOICES

    @override
    async def get_entity(self, entity_id: UUID) -> EntityResponse:
        invoice = await self.service.find_invoice_by_id(entity_id)
        return InvoiceResponse.from_orm_model(invoice)
