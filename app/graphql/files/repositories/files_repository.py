from uuid import UUID

from commons.db.models import Check, Invoice, Order, Quote
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.v2.core.customers.models.customer import CustomerV2
from app.graphql.v2.core.factories.models.factory import FactoryV2
from app.graphql.v2.core.products.models.product import ProductV2


class FilesRepository:
    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__()
        self.context = context_wrapper.get()
        self.session = session

    async def get_linked_quotes(self, file_id: UUID) -> list[Quote]:
        stmt = (
            select(Quote)
            .where(
                Quote.id.in_(
                    select(text("entity_id"))
                    .select_from(text("files.file_entity_details"))
                    .where(text("file_id = :file_id"))
                    .where(text("entity_type = 'quotes'"))
                )
            )
            .params(file_id=file_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_linked_orders(self, file_id: UUID) -> list[Order]:
        stmt = (
            select(Order)
            .where(
                Order.id.in_(
                    select(text("entity_id"))
                    .select_from(text("files.file_entity_details"))
                    .where(text("file_id = :file_id"))
                    .where(text("entity_type = 'orders'"))
                )
            )
            .params(file_id=file_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_linked_invoices(self, file_id: UUID) -> list[Invoice]:
        stmt = (
            select(Invoice)
            .where(
                Invoice.id.in_(
                    select(text("entity_id"))
                    .select_from(text("files.file_entity_details"))
                    .where(text("file_id = :file_id"))
                    .where(text("entity_type = 'invoices'"))
                )
            )
            .params(file_id=file_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_linked_checks(self, file_id: UUID) -> list[Check]:
        stmt = (
            select(Check)
            .where(
                Check.id.in_(
                    select(text("entity_id"))
                    .select_from(text("files.file_entity_details"))
                    .where(text("file_id = :file_id"))
                    .where(text("entity_type = 'checks'"))
                )
            )
            .params(file_id=file_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_linked_customers(self, file_id: UUID) -> list[CustomerV2]:
        stmt = (
            select(CustomerV2)
            .where(
                CustomerV2.id.in_(
                    select(text("entity_id"))
                    .select_from(text("files.file_entity_details"))
                    .where(text("file_id = :file_id"))
                    .where(text("entity_type = 'customers'"))
                )
            )
            .params(file_id=file_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_linked_factories(self, file_id: UUID) -> list[FactoryV2]:
        stmt = (
            select(FactoryV2)
            .where(
                FactoryV2.id.in_(
                    select(text("entity_id"))
                    .select_from(text("files.file_entity_details"))
                    .where(text("file_id = :file_id"))
                    .where(text("entity_type = 'factories'"))
                )
            )
            .params(file_id=file_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_linked_products(self, file_id: UUID) -> list[ProductV2]:
        stmt = (
            select(ProductV2)
            .where(
                ProductV2.id.in_(
                    select(text("entity_id"))
                    .select_from(text("files.file_entity_details"))
                    .where(text("file_id = :file_id"))
                    .where(text("entity_type = 'products'"))
                )
            )
            .params(file_id=file_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
