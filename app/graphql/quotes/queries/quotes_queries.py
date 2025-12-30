from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.quotes.services.quote_service import QuoteService
from app.graphql.quotes.strawberry.quote_lite_response import QuoteLiteResponse
from app.graphql.quotes.strawberry.quote_response import QuoteResponse


@strawberry.type
class QuotesQueries:
    @strawberry.field
    @inject
    async def quote(
        self,
        id: UUID,
        service: Injected[QuoteService],
    ) -> QuoteResponse:
        quote = await service.find_quote_by_id(id)
        return QuoteResponse.from_orm_model(quote)

    @strawberry.field
    @inject
    async def quote_search(
        self,
        service: Injected[QuoteService],
        search_term: str,
        limit: int = 20,
    ) -> list[QuoteLiteResponse]:
        return QuoteLiteResponse.from_orm_model_list(
            await service.search_quotes(search_term, limit)
        )
