from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.core.products.product import Product, ProductCategory
from commons.db.v6.crm.links.entity_type import EntityType
from sqlalchemy.orm import joinedload, lazyload

from app.errors.common_errors import NotFoundError
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

    async def get_by_id(self, product_id: UUID) -> Product:
        product = await self.repository.get_by_id(
            product_id,
            options=[
                joinedload(Product.factory),
                joinedload(Product.category),
                joinedload(Product.uom),
                joinedload(Product.category).joinedload(ProductCategory.parent),
                joinedload(Product.category).joinedload(ProductCategory.grandparent),
                lazyload("*"),
            ],
        )
        if not product:
            raise NotFoundError(f"Product with id {product_id} not found")
        return product

    async def create(self, product_input: ProductInput) -> Product:
        product = await self.repository.create(product_input.to_orm_model())
        return await self.get_by_id(product.id)

    async def update(self, product_id: UUID, product_input: ProductInput) -> Product:
        product = product_input.to_orm_model()
        product.id = product_id
        _ = await self.repository.update(product)
        return await self.get_by_id(product.id)

    async def delete(self, product_id: UUID) -> bool:
        if not await self.repository.exists(product_id):
            raise NotFoundError(f"Product with id {product_id} not found")
        return await self.repository.delete(product_id)

    async def search_products(
        self,
        search_term: str,
        factory_id: UUID | None,
        product_category_ids: list[UUID] | None,
        limit: int = 20,
    ) -> list[Product]:
        return await self.repository.search_by_fpn(
            search_term, factory_id, product_category_ids, limit
        )

    async def search_product_categories(
        self, search_term: str, factory_id: UUID | None, limit: int = 20
    ) -> list[ProductCategory]:
        return await self.repository.search_product_categories(
            search_term, factory_id, limit
        )

    async def find_by_entity(
        self, entity_type: EntityType, entity_id: UUID
    ) -> list[Product]:
        return await self.repository.find_by_entity(entity_type, entity_id)
