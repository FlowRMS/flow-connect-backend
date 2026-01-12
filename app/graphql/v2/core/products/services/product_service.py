from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.core.products.product import Product, ProductCategory
from commons.db.v6.core.products.product_cpn import ProductCpn
from commons.db.v6.crm.links.entity_type import EntityType
from sqlalchemy.orm import joinedload, lazyload

from app.errors.common_errors import NameAlreadyExistsError, NotFoundError
from app.graphql.v2.core.products.repositories.product_cpn_repository import (
    ProductCpnRepository,
)
from app.graphql.v2.core.products.repositories.products_repository import (
    ProductsRepository,
)
from app.graphql.v2.core.products.strawberry.product_input import ProductInput


class ProductService:
    def __init__(
        self,
        repository: ProductsRepository,
        cpn_repository: ProductCpnRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.cpn_repository = cpn_repository
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
        if await self.repository.factory_part_number_exists(
            product_input.factory_part_number, product_input.factory_id
        ):
            raise NameAlreadyExistsError(product_input.factory_part_number)
        product = await self.repository.create(product_input.to_orm_model())
        return await self.get_by_id(product.id)

    async def bulk_create(self, product_inputs: list[ProductInput]) -> list[Product]:
        if not product_inputs:
            return []

        fpn_pairs = [
            (inp.factory_part_number, inp.factory_id) for inp in product_inputs
        ]
        existing = await self.repository.get_existing_factory_part_numbers(fpn_pairs)

        valid_inputs = [
            inp
            for inp in product_inputs
            if (inp.factory_part_number, inp.factory_id) not in existing
        ]
        if not valid_inputs:
            return []

        entities = [inp.to_orm_model() for inp in valid_inputs]
        created = await self.repository.bulk_create(entities)
        return created

    async def get_existing_products(
        self,
        fpn_factory_pairs: list[tuple[str, UUID]],
    ) -> list[Product]:
        if not fpn_factory_pairs:
            return []
        return await self.repository.get_existing_products(fpn_factory_pairs)

    async def bulk_update(
        self,
        inputs_with_entities: list[tuple[ProductInput, Product]],
    ) -> list[Product]:
        if not inputs_with_entities:
            return []

        updated_entities: list[Product] = []
        for product_input, existing_product in inputs_with_entities:
            existing_product.unit_price = product_input.unit_price
            existing_product.default_commission_rate = (
                product_input.default_commission_rate
            )
            existing_product.description = product_input.description
            existing_product.upc = product_input.upc
            existing_product.min_order_qty = product_input.min_order_qty
            existing_product.lead_time = product_input.lead_time
            existing_product.unit_price_discount_rate = (
                product_input.unit_price_discount_rate
            )
            existing_product.commission_discount_rate = (
                product_input.commission_discount_rate
            )
            existing_product.approval_needed = product_input.approval_needed
            existing_product.approval_date = product_input.approval_date
            existing_product.approval_comments = product_input.approval_comments
            updated_entities.append(existing_product)

        _ = await self.repository.bulk_update(updated_entities)
        await self._process_cpns(inputs_with_entities)
        return updated_entities

    async def _process_cpns(
        self,
        inputs_with_entities: list[tuple[ProductInput, Product]],
    ) -> None:
        cpn_pairs: list[tuple[UUID, UUID]] = []
        for product_input, existing_product in inputs_with_entities:
            if product_input.cpns:
                for cpn_input in product_input.cpns:
                    cpn_pairs.append((existing_product.id, cpn_input.customer_id))

        if not cpn_pairs:
            return

        existing_cpns = await self.cpn_repository.find_existing_cpns(cpn_pairs)

        cpns_to_create: list[ProductCpn] = []
        for product_input, existing_product in inputs_with_entities:
            if not product_input.cpns:
                continue
            for cpn_input in product_input.cpns:
                key = (existing_product.id, cpn_input.customer_id)
                existing_cpn = existing_cpns.get(key)
                if existing_cpn:
                    existing_cpn.customer_part_number = cpn_input.customer_part_number
                    existing_cpn.unit_price = cpn_input.unit_price
                    existing_cpn.commission_rate = cpn_input.commission_rate
                else:
                    new_cpn = cpn_input.to_orm_model()
                    new_cpn.product_id = existing_product.id
                    cpns_to_create.append(new_cpn)

        if cpns_to_create:
            _ = await self.cpn_repository.bulk_create(cpns_to_create)

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

    async def find_by_factory_id(
        self, factory_id: UUID, limit: int = 25
    ) -> list[Product]:
        return await self.repository.find_by_factory_id(factory_id, limit)
