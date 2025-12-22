from uuid import UUID

from commons.db.v6 import Customer
from commons.db.v6.commission import Check, Invoice, Order
from commons.db.v6.core.factories.factory import Factory
from commons.db.v6.core.products.product import Product
from commons.db.v6.crm import Quote
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper


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

    async def get_linked_customers(self, file_id: UUID) -> list[Customer]:
        stmt = (
            select(Customer)
            .where(
                Customer.id.in_(
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

    async def get_linked_factories(self, file_id: UUID) -> list[Factory]:
        stmt = (
            select(Factory)
            .where(
                Factory.id.in_(
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

    async def get_linked_products(self, file_id: UUID) -> list[Product]:
        stmt = (
            select(Product)
            .where(
                Product.id.in_(
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
