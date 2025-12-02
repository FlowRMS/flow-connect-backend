from uuid import UUID

from commons.auth import AuthInfo
from commons.db.models import Invoice

from app.graphql.invoices.repositories.invoices_repository import InvoicesRepository


class InvoiceService:
    """Service for Invoices entity business logic."""

    def __init__(
        self,
        repository: InvoicesRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def search_invoices(self, search_term: str, limit: int = 20) -> list[Invoice]:
        """
        Search invoices by invoice number.

        Args:
            search_term: The search term to match against invoice number
            limit: Maximum number of invoices to return (default: 20)

        Returns:
            List of Invoice objects matching the search criteria
        """
        return await self.repository.search_by_invoice_number(search_term, limit)

    async def find_invoices_by_job_id(self, job_id: UUID) -> list[Invoice]:
        """Find all invoices linked to the given job ID."""
        return await self.repository.find_by_job_id(job_id)
