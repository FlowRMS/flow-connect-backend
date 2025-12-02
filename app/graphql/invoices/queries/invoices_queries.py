import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.invoices.services.invoice_service import InvoiceService
from app.graphql.invoices.strawberry.invoice_response import InvoiceResponse


@strawberry.type
class InvoicesQueries:
    """GraphQL queries for Invoices entity."""

    @strawberry.field
    @inject
    async def invoice_search(
        self,
        service: Injected[InvoiceService],
        search_term: str,
        limit: int = 20,
    ) -> list[InvoiceResponse]:
        """
        Search invoices by invoice number.

        Args:
            search_term: The search term to match against invoice number
            limit: Maximum number of invoices to return (default: 20)

        Returns:
            List of InvoiceResponse objects matching the search criteria
        """
        return InvoiceResponse.from_orm_model_list(
            await service.search_invoices(search_term, limit)
        )
