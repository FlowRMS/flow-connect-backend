from uuid import UUID

from commons.db.v6.core import Customer, Factory, Product
from commons.db.v6.crm import Quote
from commons.db.v6.user import User
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.processors import BaseProcessor, EntityContext, RepositoryEvent


class QuoteDuplicationError(Exception):
    def __init__(self, missing_entities: list[str]) -> None:
        self.missing_entities = missing_entities
        message = "Cannot duplicate quote: " + "; ".join(missing_entities)
        super().__init__(message)


class ValidateQuoteReferencesProcessor(BaseProcessor[Quote]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_CREATE]

    async def process(self, context: EntityContext[Quote]) -> None:
        quote = context.entity
        missing_entities: list[str] = []

        await self._validate_customers(quote, missing_entities)

        factory_ids, product_ids, end_user_ids, user_ids = (
            self._collect_detail_entity_ids(quote)
        )

        await self._validate_factories(factory_ids, missing_entities)
        await self._validate_products(product_ids, missing_entities)
        await self._validate_end_users(end_user_ids, missing_entities)
        await self._validate_users(user_ids, missing_entities)

        if missing_entities:
            logger.warning(
                f"Quote creation blocked - missing entities: {missing_entities}"
            )
            raise QuoteDuplicationError(missing_entities)

    async def _validate_customers(self, quote: Quote, missing: list[str]) -> None:
        if quote.sold_to_customer_id:
            result = await self.session.execute(
                select(Customer.id).where(Customer.id == quote.sold_to_customer_id)
            )
            if not result.scalar_one_or_none():
                missing.append(
                    f"Sold-to customer (ID: {quote.sold_to_customer_id}) "
                    "no longer exists"
                )

        if quote.bill_to_customer_id:
            result = await self.session.execute(
                select(Customer.id).where(Customer.id == quote.bill_to_customer_id)
            )
            if not result.scalar_one_or_none():
                missing.append(
                    f"Bill-to customer (ID: {quote.bill_to_customer_id}) "
                    "no longer exists"
                )

    def _collect_detail_entity_ids(
        self, quote: Quote
    ) -> tuple[set[UUID], set[UUID], set[UUID], set[UUID]]:
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

        return factory_ids, product_ids, end_user_ids, user_ids

    async def _validate_factories(
        self, factory_ids: set[UUID], missing: list[str]
    ) -> None:
        if not factory_ids:
            return
        result = await self.session.execute(
            select(Factory.id).where(Factory.id.in_(factory_ids))
        )
        existing = {row[0] for row in result.fetchall()}
        for fid in factory_ids - existing:
            missing.append(f"Factory (ID: {fid}) no longer exists")

    async def _validate_products(
        self, product_ids: set[UUID], missing: list[str]
    ) -> None:
        if not product_ids:
            return
        result = await self.session.execute(
            select(Product.id).where(Product.id.in_(product_ids))
        )
        existing = {row[0] for row in result.fetchall()}
        for pid in product_ids - existing:
            missing.append(f"Product (ID: {pid}) no longer exists")

    async def _validate_end_users(
        self, end_user_ids: set[UUID], missing: list[str]
    ) -> None:
        if not end_user_ids:
            return
        result = await self.session.execute(
            select(Customer.id).where(Customer.id.in_(end_user_ids))
        )
        existing = {row[0] for row in result.fetchall()}
        for cid in end_user_ids - existing:
            missing.append(f"End user customer (ID: {cid}) no longer exists")

    async def _validate_users(self, user_ids: set[UUID], missing: list[str]) -> None:
        if not user_ids:
            return
        result = await self.session.execute(
            select(User.id).where(User.id.in_(user_ids))
        )
        existing = {row[0] for row in result.fetchall()}
        for uid in user_ids - existing:
            missing.append(f"Rep user (ID: {uid}) no longer exists")
