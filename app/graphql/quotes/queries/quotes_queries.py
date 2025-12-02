import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.quotes.services.quote_service import QuoteService
from app.graphql.quotes.strawberry.quote_response import QuoteResponse


@strawberry.type
class QuotesQueries:
    """GraphQL queries for Quotes entity."""

    @strawberry.field
    @inject
    async def quote_search(
        self,
        service: Injected[QuoteService],
        search_term: str,
        limit: int = 20,
    ) -> list[QuoteResponse]:
        """
        Search quotes by quote number.

        Args:
            search_term: The search term to match against quote number
            limit: Maximum number of quotes to return (default: 20)

        Returns:
            List of QuoteResponse objects matching the search criteria
        """
        return QuoteResponse.from_orm_model_list(
            await service.search_quotes(search_term, limit)
        )
