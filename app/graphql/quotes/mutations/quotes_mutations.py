from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.quotes.services.quote_service import QuoteService
from app.graphql.quotes.strawberry.quote_input import QuoteInput
from app.graphql.quotes.strawberry.quote_response import QuoteResponse


@strawberry.type
class QuotesMutations:
    @strawberry.mutation
    @inject
    async def create_quote(
        self,
        input: QuoteInput,
        service: Injected[QuoteService],
    ) -> QuoteResponse:
        quote = await service.create_quote(quote_input=input)
        return QuoteResponse.from_orm_model(quote)

    @strawberry.mutation
    @inject
    async def update_quote(
        self,
        input: QuoteInput,
        service: Injected[QuoteService],
    ) -> QuoteResponse:
        quote = await service.update_quote(quote_input=input)
        return QuoteResponse.from_orm_model(quote)

    @strawberry.mutation
    @inject
    async def delete_quote(
        self,
        id: UUID,
        service: Injected[QuoteService],
    ) -> bool:
        return await service.delete_quote(quote_id=id)

    @strawberry.mutation
    @inject
    async def create_quote_from_pre_opportunity(
        self,
        pre_opportunity_id: UUID,
        quote_number: str,
        service: Injected[QuoteService],
        pre_opportunity_detail_ids: list[UUID] | None = None,
    ) -> QuoteResponse:
        quote = await service.create_quote_from_pre_opportunity(
            pre_opportunity_id=pre_opportunity_id,
            quote_number=quote_number,
            pre_opportunity_detail_ids=pre_opportunity_detail_ids,
        )
        return QuoteResponse.from_orm_model(quote)

    @strawberry.mutation
    @inject
    async def duplicate_quote(
        self,
        source_quote_id: UUID,
        new_quote_number: str,
        service: Injected[QuoteService],
    ) -> QuoteResponse:
        quote = await service.duplicate_quote(
            source_quote_id=source_quote_id,
            new_quote_number=new_quote_number,
        )
        return QuoteResponse.from_orm_model(quote)
