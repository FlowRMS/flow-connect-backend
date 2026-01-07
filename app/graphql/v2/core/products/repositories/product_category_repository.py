from uuid import UUID

from commons.db.v6.core.products.product_category import ProductCategory
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class ProductCategoryRepository(BaseRepository[ProductCategory]):
    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, ProductCategory)

    async def name_exists(self, factory_id: UUID | None, name: str) -> bool:
        stmt = select(ProductCategory).where(
            ProductCategory.title == name,
        )
        if factory_id is None:
            stmt = stmt.where(ProductCategory.factory_id.is_(None))
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None

    async def get_by_factory_id(self, factory_id: UUID) -> list[ProductCategory]:
        stmt = select(ProductCategory).where(ProductCategory.factory_id == factory_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_with_filters(
        self,
        factory_id: UUID | None = None,
        parent_id: UUID | None = None,
        grandparent_id: UUID | None = None,
    ) -> list[ProductCategory]:
        stmt = select(ProductCategory)
        if factory_id is not None:
            stmt = stmt.where(ProductCategory.factory_id == factory_id)
        if parent_id is not None:
            stmt = stmt.where(ProductCategory.parent_id == parent_id)
        if grandparent_id is not None:
            stmt = stmt.where(ProductCategory.grandparent_id == grandparent_id)
        result = await self.session.execute(
            stmt.options(
                joinedload(ProductCategory.parent),
                joinedload(ProductCategory.grandparent),
                selectinload(ProductCategory.children),
            )
        )
        return list(result.scalars().unique().all())

    async def get_children(self, parent_id: UUID) -> list[ProductCategory]:
        """Get all categories where parent_id equals the given ID."""
        stmt = select(ProductCategory).where(ProductCategory.parent_id == parent_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_root_categories(
        self, factory_id: UUID | None = None
    ) -> list[ProductCategory]:
        """Get all categories with no parent (Level 1 / root categories)."""
        stmt = select(ProductCategory).where(ProductCategory.parent_id.is_(None))
        if factory_id is not None:
            stmt = stmt.where(ProductCategory.factory_id == factory_id)
        result = await self.session.execute(
            stmt.options(
                joinedload(ProductCategory.parent),
                joinedload(ProductCategory.grandparent),
                selectinload(ProductCategory.children),
            )
        )
        return list(result.scalars().unique().all())
