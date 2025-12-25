from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.quotes.services.quote_service import QuoteService
from app.graphql.quotes.strawberry.quote_full_response import QuoteFullResponse
from app.graphql.quotes.strawberry.quote_lite_response import QuoteLiteResponse


@strawberry.type
class QuotesQueries:
    @strawberry.field
    @inject
    async def quote(
        self,
        id: UUID,
        service: Injected[QuoteService],
    ) -> QuoteFullResponse:
        quote = await service.find_quote_by_id(id)
        return QuoteFullResponse.from_orm_model(quote)

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
