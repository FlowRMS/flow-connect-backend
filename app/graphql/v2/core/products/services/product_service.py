from uuid import UUID

from commons.auth import AuthInfo

from app.errors.common_errors import NotFoundError
from app.graphql.links.models.entity_type import EntityType
from app.graphql.v2.core.products.models import ProductCategoryV2, ProductV2
from app.graphql.v2.core.products.repositories.products_repository import (
    ProductsRepository,
)
from app.graphql.v2.core.products.strawberry.product_input import ProductInput


class ProductService:
    def __init__(
        self,
        repository: ProductsRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_by_id(self, product_id: UUID) -> ProductV2:
        product = await self.repository.get_by_id(product_id)
        if not product:
            raise NotFoundError(f"ProductV2 with id {product_id} not found")
        return product

    async def create(self, product_input: ProductInput) -> ProductV2:
        return await self.repository.create(product_input.to_orm_model())

    async def update(self, product_id: UUID, product_input: ProductInput) -> ProductV2:
        product = product_input.to_orm_model()
        product.id = product_id
        return await self.repository.update(product)

    async def delete(self, product_id: UUID) -> bool:
        if not await self.repository.exists(product_id):
            raise NotFoundError(f"ProductV2 with id {product_id} not found")
        return await self.repository.delete(product_id)

    async def search_products(
        self,
        search_term: str,
        factory_id: UUID | None,
        product_category_ids: list[UUID],
        limit: int = 20,
    ) -> list[ProductV2]:
        return await self.repository.search_by_fpn(
            search_term, factory_id, product_category_ids, limit
        )

    async def search_product_categories(
        self, search_term: str, factory_id: UUID | None, limit: int = 20
    ) -> list[ProductCategoryV2]:
        return await self.repository.search_product_categories(
            search_term, factory_id, limit
        )

    async def find_by_entity(
        self, entity_type: EntityType, entity_id: UUID
    ) -> list[ProductV2]:
        return await self.repository.find_by_entity(entity_type, entity_id)
