from uuid import UUID

from commons.db.v6.core.products.product_uom import ProductUom

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.products.repositories.product_uom_repository import (
    ProductUomRepository,
)
from app.graphql.v2.core.products.strawberry.product_uom_input import ProductUomInput


class ProductUomService:
    def __init__(self, repository: ProductUomRepository) -> None:
        super().__init__()
        self.repository = repository

    async def get_by_id(self, uom_id: UUID) -> ProductUom:
        uom = await self.repository.get_by_id(uom_id)
        if not uom:
            raise NotFoundError(f"ProductUom with id {uom_id} not found")
        return uom

    async def list_all(self) -> list[ProductUom]:
        return await self.repository.list_all()

    async def create(self, uom_input: ProductUomInput) -> ProductUom:
        return await self.repository.create(uom_input.to_orm_model())

    async def update(self, uom_id: UUID, uom_input: ProductUomInput) -> ProductUom:
        uom = uom_input.to_orm_model()
        uom.id = uom_id
        return await self.repository.update(uom)

    async def delete(self, uom_id: UUID) -> bool:
        if not await self.repository.exists(uom_id):
            raise NotFoundError(f"ProductUom with id {uom_id} not found")
        return await self.repository.delete(uom_id)
