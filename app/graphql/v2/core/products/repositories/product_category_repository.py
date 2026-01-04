from uuid import UUID

from commons.db.v6.core.products.product_category import ProductCategory
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class ProductCategoryRepository(BaseRepository[ProductCategory]):
    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, ProductCategory)

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
            )
        )
        return list(result.scalars().all())
