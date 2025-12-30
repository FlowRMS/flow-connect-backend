from uuid import UUID

from commons.db.v6.core.products.product_cpn import ProductCpn

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.products.repositories.product_cpn_repository import (
    ProductCpnRepository,
)
from app.graphql.v2.core.products.strawberry.product_cpn_input import ProductCpnInput


class ProductCpnService:
    def __init__(self, repository: ProductCpnRepository) -> None:
        super().__init__()
        self.repository = repository

    async def get_by_id(self, cpn_id: UUID) -> ProductCpn:
        cpn = await self.repository.get_by_id_with_relations(cpn_id)
        if not cpn:
            raise NotFoundError(f"ProductCpn with id {cpn_id} not found")
        return cpn

    async def list_by_product_id(self, product_id: UUID) -> list[ProductCpn]:
        return await self.repository.list_by_product_id(product_id)

    async def find_cpn_by_product_and_customer(
        self, product_id: UUID, customer_id: UUID
    ) -> ProductCpn | None:
        return await self.repository.find_cpn_by_product_and_customer(
            product_id, customer_id
        )

    async def create(self, cpn_input: ProductCpnInput) -> ProductCpn:
        cpn = await self.repository.create(cpn_input.to_orm_model())
        return await self.get_by_id(cpn.id)

    async def update(self, cpn_id: UUID, cpn_input: ProductCpnInput) -> ProductCpn:
        cpn = cpn_input.to_orm_model()
        cpn.id = cpn_id
        _ = await self.repository.update(cpn)
        return await self.get_by_id(cpn_id)

    async def delete(self, cpn_id: UUID) -> bool:
        if not await self.repository.exists(cpn_id):
            raise NotFoundError(f"ProductCpn with id {cpn_id} not found")
        return await self.repository.delete(cpn_id)
