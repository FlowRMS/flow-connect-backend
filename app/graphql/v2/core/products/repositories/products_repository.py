from typing import Any
from uuid import UUID

from commons.db.v6 import RbacResourceEnum, User
from commons.db.v6.core import Product, ProductCategory
from commons.db.v6.core.factories.factory import Factory
from commons.db.v6.core.products.product_uom import ProductUom
from commons.db.v6.crm.links.entity_type import EntityType
from sqlalchemy import Select, select
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.core.context_wrapper import ContextWrapper
from app.core.processors.executor import ProcessorExecutor
from app.graphql.base_repository import BaseRepository
from app.graphql.v2.core.products.processors.validate_product_category_processor import (
    ValidateProductCategoryProcessor,
)
from app.graphql.v2.core.products.strawberry.product_landing_page_response import (
    ProductLandingPageResponse,
)


class ProductsRepository(BaseRepository[Product]):
    entity_type = EntityType.PRODUCT
    landing_model = ProductLandingPageResponse
    rbac_resource: RbacResourceEnum | None = RbacResourceEnum.PRODUCT

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
        processor_executor: ProcessorExecutor,
        validate_product_category_processor: ValidateProductCategoryProcessor,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            Product,
            processor_executor=processor_executor,
            processor_executor_classes=[validate_product_category_processor],
        )

    def paginated_stmt(self) -> Select[Any]:
        return (
            select(
                Product.id,
                Product.created_at.label("created_at"),
                User.full_name.label("created_by"),
                Product.factory_part_number,
                Product.unit_price,
                Product.default_commission_rate,
                Product.published,
                Product.approval_needed,
                Product.description,
                Factory.title.label("factory_title"),
                ProductCategory.title.label("category_title"),
                ProductUom.title.label("uom_title"),
                Product.tags,
                array([Product.created_by_id]).label("user_ids"),
            )
            .select_from(Product)
            .options(lazyload("*"))
            .join(User, User.id == Product.created_by_id)
            .join(Factory, Factory.id == Product.factory_id)
            .outerjoin(
                ProductCategory, ProductCategory.id == Product.product_category_id
            )
            .outerjoin(ProductUom, ProductUom.id == Product.product_uom_id)
        )

    async def search_by_fpn(
        self,
        search_term: str,
        factory_id: UUID | None,
        product_category_ids: list[UUID] | None = None,
        limit: int = 20,
    ) -> list[Product]:
        """
        Search products by factory part number using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against factory part number
            factory_id: The UUID of the factory to filter products by (optional)
            product_category_id: The UUID of the product category to filter by (optional)
            limit: Maximum number of products to return (default: 20)

        Returns:
            List of Product objects matching the search criteria
        """
        stmt = (
            select(Product)
            .where(Product.factory_part_number.ilike(f"%{search_term}%"))
            .limit(limit)
        )

        if factory_id is not None:
            stmt = stmt.where(Product.factory_id == factory_id)

        if product_category_ids:
            stmt = stmt.where(Product.product_category_id.in_(product_category_ids))

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_product_categories(
        self, search_term: str, factory_id: UUID | None, limit: int = 20
    ) -> list[ProductCategory]:
        """
        Search product categories by title using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against category title
            factory_id: The UUID of the factory to filter categories by (optional)
            limit: Maximum number of categories to return (default: 20)

        Returns:
            List of ProductCategory objects matching the search criteria
        """
        stmt = (
            select(ProductCategory)
            .where(ProductCategory.title.ilike(f"%{search_term}%"))
            .limit(limit)
        )

        if factory_id is not None:
            stmt = stmt.where(ProductCategory.factory_id == factory_id)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
