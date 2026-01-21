from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.crm import Quote
from commons.db.v6.crm.links.entity_type import EntityType

from app.errors.common_errors import NameAlreadyExistsError, NotFoundError
from app.graphql.pre_opportunities.repositories.pre_opportunities_repository import (
    PreOpportunitiesRepository,
)
from app.graphql.quotes.factories.quote_factory import QuoteFactory
from app.graphql.quotes.repositories.quotes_repository import QuotesRepository
from app.graphql.quotes.strawberry.quote_input import QuoteInput


class QuoteService:
    def __init__(
        self,
        repository: QuotesRepository,
        pre_opportunity_repository: PreOpportunitiesRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.pre_opportunity_repository = pre_opportunity_repository
        self.auth_info = auth_info

    async def find_quote_by_id(self, quote_id: UUID) -> Quote:
        return await self.repository.find_quote_by_id(quote_id)

    async def create_quote(self, quote_input: QuoteInput) -> Quote:
        if await self.repository.quote_number_exists(quote_input.quote_number):
            raise NameAlreadyExistsError(quote_input.quote_number)

        quote = quote_input.to_orm_model()
        return await self.repository.create_with_balance(quote)

    async def update_quote(self, quote_input: QuoteInput) -> Quote:
        if quote_input.id is None:
            raise ValueError("ID must be provided for update")

        quote = quote_input.to_orm_model()
        quote.id = quote_input.id
        return await self.repository.update_with_balance(quote)

    async def delete_quote(self, quote_id: UUID) -> bool:
        if not await self.repository.exists(quote_id):
            raise NotFoundError(str(quote_id))
        return await self.repository.delete(quote_id)

    async def create_quote_from_pre_opportunity(
        self,
        pre_opportunity_id: UUID,
        quote_number: str,
        pre_opportunity_detail_ids: list[UUID] | None = None,
    ) -> Quote:
        pre_opp = await self.pre_opportunity_repository.get_by_id(pre_opportunity_id)
        if not pre_opp:
            raise NotFoundError(str(pre_opportunity_id))

        if await self.repository.quote_number_exists(quote_number):
            raise NameAlreadyExistsError(quote_number)

        quote = QuoteFactory.from_pre_opportunity(pre_opp, quote_number)
        created_quote = await self.repository.create_with_balance(quote)

        if pre_opportunity_detail_ids:
            await self.pre_opportunity_repository.update_detail_quote_ids(
                detail_ids=pre_opportunity_detail_ids,
                quote_id=created_quote.id,
            )

        return created_quote

    async def duplicate_quote(
        self,
        source_quote_id: UUID,
        new_quote_number: str,
    ) -> Quote:
        source_quote = await self.find_quote_by_id(source_quote_id)

        if await self.repository.quote_number_exists(new_quote_number):
            raise NameAlreadyExistsError(new_quote_number)

        new_quote = QuoteFactory.duplicate(source_quote, new_quote_number)
        return await self.repository.create_with_balance(new_quote)

    async def search_quotes(self, search_term: str, limit: int = 20) -> list[Quote]:
        return await self.repository.search_by_quote_number(search_term, limit)

    async def find_quotes_by_job_id(self, job_id: UUID) -> list[Quote]:
        return await self.repository.find_by_job_id(job_id)

    async def find_by_entity(
        self, entity_type: EntityType, entity_id: UUID
    ) -> list[Quote]:
        return await self.repository.find_by_entity(entity_type, entity_id)

    async def find_by_sold_to_customer_id(self, customer_id: UUID) -> list[Quote]:
        return await self.repository.find_by_sold_to_customer_id(customer_id)
