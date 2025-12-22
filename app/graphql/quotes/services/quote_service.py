from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.quotes import Quote

from app.graphql.quotes.repositories.quotes_repository import QuotesRepository


class QuoteService:
    """Service for Quotes entity business logic."""

    def __init__(
        self,
        repository: QuotesRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def search_quotes(self, search_term: str, limit: int = 20) -> list[Quote]:
        """
        Search quotes by quote number.

        Args:
            search_term: The search term to match against quote number
            limit: Maximum number of quotes to return (default: 20)

        Returns:
            List of Quote objects matching the search criteria
        """
        return await self.repository.search_by_quote_number(search_term, limit)

    async def find_quotes_by_job_id(self, job_id: UUID) -> list[Quote]:
        """Find all quotes linked to the given job ID."""
        return await self.repository.find_by_job_id(job_id)

    async def find_by_entity(
        self, entity_type: EntityType, entity_id: UUID
    ) -> list[Quote]:
        """Find all quotes linked to a specific entity."""
        return await self.repository.find_by_entity(entity_type, entity_id)
