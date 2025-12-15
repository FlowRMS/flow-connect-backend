from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.links.models.entity_type import EntityType
from app.graphql.v2.core.products.models import ProductCategoryV2, ProductV2


class ProductsRepository(BaseRepository[ProductV2]):
    """Repository for Products entity."""

    entity_type = EntityType.PRODUCT

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, ProductV2)

    async def search_by_fpn(
        self,
        search_term: str,
        factory_id: UUID | None,
        product_category_ids: list[UUID],
        limit: int = 20,
    ) -> list[ProductV2]:
        """
        Search products by factory part number using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against factory part number
            factory_id: The UUID of the factory to filter products by (optional)
            product_category_id: The UUID of the product category to filter by (optional)
            limit: Maximum number of products to return (default: 20)

        Returns:
            List of ProductV2 objects matching the search criteria
        """
        stmt = (
            select(ProductV2)
            .where(ProductV2.factory_part_number.ilike(f"%{search_term}%"))
            .limit(limit)
        )

        if factory_id is not None:
            stmt = stmt.where(ProductV2.factory_id == factory_id)

        if product_category_ids:
            stmt = stmt.where(ProductV2.product_category_id.in_(product_category_ids))

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_product_categories(
        self, search_term: str, factory_id: UUID | None, limit: int = 20
    ) -> list[ProductCategoryV2]:
        """
        Search product categories by title using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against category title
            factory_id: The UUID of the factory to filter categories by (optional)
            limit: Maximum number of categories to return (default: 20)

        Returns:
            List of ProductCategoryV2 objects matching the search criteria
        """
        stmt = (
            select(ProductCategoryV2)
            .where(ProductCategoryV2.title.ilike(f"%{search_term}%"))
            .limit(limit)
        )

        if factory_id is not None:
            stmt = stmt.where(ProductCategoryV2.factory_id == factory_id)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
