from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6 import Customer

# from commons.db.models import Check, Invoice, Order, Quote
from commons.db.v6.commission import Check, Invoice, Order
from commons.db.v6.core.factories.factory import Factory
from commons.db.v6.core.products.product import Product
from commons.db.v6.crm import Quote

from app.graphql.files.repositories.files_repository import FilesRepository


class FilesService:
    def __init__(
        self,
        repository: FilesRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_linked_quotes(self, file_id: UUID) -> list[Quote]:
        return await self.repository.get_linked_quotes(file_id)

    async def get_linked_orders(self, file_id: UUID) -> list[Order]:
        return await self.repository.get_linked_orders(file_id)

    async def get_linked_invoices(self, file_id: UUID) -> list[Invoice]:
        return await self.repository.get_linked_invoices(file_id)

    async def get_linked_checks(self, file_id: UUID) -> list[Check]:
        return await self.repository.get_linked_checks(file_id)

    async def get_linked_customers(self, file_id: UUID) -> list[Customer]:
        return await self.repository.get_linked_customers(file_id)

    async def get_linked_factories(self, file_id: UUID) -> list[Factory]:
        return await self.repository.get_linked_factories(file_id)

    async def get_linked_products(self, file_id: UUID) -> list[Product]:
        return await self.repository.get_linked_products(file_id)
