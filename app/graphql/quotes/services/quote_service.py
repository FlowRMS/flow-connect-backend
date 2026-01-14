from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.crm import Quote
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.core import Customer, Factory, Product
from commons.db.v6.user import User
from loguru import logger
from sqlalchemy import select

from app.errors.common_errors import NameAlreadyExistsError, NotFoundError
from app.graphql.pre_opportunities.repositories.pre_opportunities_repository import (
    PreOpportunitiesRepository,
)
from app.graphql.quotes.factories.quote_factory import QuoteFactory
from app.graphql.quotes.repositories.quotes_repository import QuotesRepository
from app.graphql.quotes.strawberry.quote_input import QuoteInput


class QuoteDuplicationError(Exception):
    """Raised when quote duplication fails due to missing referenced entities."""

    def __init__(self, missing_entities: list[str]):
        self.missing_entities = missing_entities
        message = "Cannot duplicate quote: " + "; ".join(missing_entities)
        super().__init__(message)


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

        # Validate all referenced entities still exist before duplicating
        await self._validate_quote_references(source_quote)

        new_quote = QuoteFactory.duplicate(source_quote, new_quote_number)
        return await self.repository.create_with_balance(new_quote)

    async def _validate_quote_references(self, quote: Quote) -> None:
        """
        Validate that all referenced entities in a quote still exist.

        This prevents FK constraint violations when duplicating a quote
        where referenced customers, factories, products, or users have
        been deleted since the original quote was created.

        Args:
            quote: The quote to validate

        Raises:
            QuoteDuplicationError: If any referenced entities are missing
        """
        missing_entities: list[str] = []
        session = self.repository.session

        # Validate quote-level customers
        if quote.sold_to_customer_id:
            result = await session.execute(
                select(Customer.id).where(Customer.id == quote.sold_to_customer_id)
            )
            if not result.scalar_one_or_none():
                missing_entities.append(
                    f"Sold-to customer (ID: {quote.sold_to_customer_id}) no longer exists"
                )

        if quote.bill_to_customer_id:
            result = await session.execute(
                select(Customer.id).where(Customer.id == quote.bill_to_customer_id)
            )
            if not result.scalar_one_or_none():
                missing_entities.append(
                    f"Bill-to customer (ID: {quote.bill_to_customer_id}) no longer exists"
                )

        # Collect all unique IDs from details
        factory_ids: set[UUID] = set()
        product_ids: set[UUID] = set()
        end_user_ids: set[UUID] = set()
        user_ids: set[UUID] = set()

        for detail in quote.details:
            if detail.factory_id:
                factory_ids.add(detail.factory_id)
            if detail.product_id:
                product_ids.add(detail.product_id)
            if detail.end_user_id:
                end_user_ids.add(detail.end_user_id)

            for split_rate in detail.outside_split_rates:
                if split_rate.user_id:
                    user_ids.add(split_rate.user_id)

            for inside_rep in detail.inside_split_rates:
                if inside_rep.user_id:
                    user_ids.add(inside_rep.user_id)

        # Batch validate factories
        if factory_ids:
            result = await session.execute(
                select(Factory.id).where(Factory.id.in_(factory_ids))
            )
            existing_factory_ids = {row[0] for row in result.fetchall()}
            missing_factory_ids = factory_ids - existing_factory_ids
            for fid in missing_factory_ids:
                missing_entities.append(f"Factory (ID: {fid}) no longer exists")

        # Batch validate products
        if product_ids:
            result = await session.execute(
                select(Product.id).where(Product.id.in_(product_ids))
            )
            existing_product_ids = {row[0] for row in result.fetchall()}
            missing_product_ids = product_ids - existing_product_ids
            for pid in missing_product_ids:
                missing_entities.append(f"Product (ID: {pid}) no longer exists")

        # Batch validate end users (customers)
        if end_user_ids:
            result = await session.execute(
                select(Customer.id).where(Customer.id.in_(end_user_ids))
            )
            existing_customer_ids = {row[0] for row in result.fetchall()}
            missing_customer_ids = end_user_ids - existing_customer_ids
            for cid in missing_customer_ids:
                missing_entities.append(f"End user customer (ID: {cid}) no longer exists")

        # Batch validate users (for split rates)
        if user_ids:
            result = await session.execute(
                select(User.id).where(User.id.in_(user_ids))
            )
            existing_user_ids = {row[0] for row in result.fetchall()}
            missing_user_ids = user_ids - existing_user_ids
            for uid in missing_user_ids:
                missing_entities.append(f"Rep user (ID: {uid}) no longer exists")

        # Raise error if any entities are missing
        if missing_entities:
            logger.warning(
                f"Quote duplication blocked - missing entities: {missing_entities}"
            )
            raise QuoteDuplicationError(missing_entities)

    async def search_quotes(self, search_term: str, limit: int = 20) -> list[Quote]:
        return await self.repository.search_by_quote_number(search_term, limit)

    async def find_quotes_by_job_id(self, job_id: UUID) -> list[Quote]:
        return await self.repository.find_by_job_id(job_id)

    async def find_by_entity(
        self, entity_type: EntityType, entity_id: UUID
    ) -> list[Quote]:
        return await self.repository.find_by_entity(entity_type, entity_id)

    async def get_existing_quotes(self, quote_numbers: list[str]) -> list[Quote]:
        return await self.repository.get_existing_quotes(quote_numbers)

    async def find_by_sold_to_customer_id(self, customer_id: UUID) -> list[Quote]:
        return await self.repository.find_by_sold_to_customer_id(customer_id)
