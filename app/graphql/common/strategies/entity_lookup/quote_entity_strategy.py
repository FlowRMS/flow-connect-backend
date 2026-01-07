from typing import override
from uuid import UUID

from app.graphql.common.entity_source_type import EntitySourceType
from app.graphql.common.interfaces.entity_lookup_strategy import EntityLookupStrategy
from app.graphql.common.strawberry.entity_response import EntityResponse
from app.graphql.quotes.services.quote_service import QuoteService
from app.graphql.quotes.strawberry.quote_response import QuoteResponse


class QuoteEntityStrategy(EntityLookupStrategy):
    def __init__(self, service: QuoteService) -> None:
        super().__init__()
        self.service = service

    @override
    def get_supported_source_type(self) -> EntitySourceType:
        return EntitySourceType.QUOTES

    @override
    async def get_entity(self, entity_id: UUID) -> EntityResponse:
        quote = await self.service.find_quote_by_id(entity_id)
        return QuoteResponse.from_orm_model(quote)
