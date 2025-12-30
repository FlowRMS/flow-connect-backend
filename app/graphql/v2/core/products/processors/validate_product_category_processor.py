from uuid import UUID

from commons.db.v6.core.products.product import Product
from commons.db.v6.core.products.product_category import ProductCategory
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.processors import (
    BaseProcessor,
    EntityContext,
    RepositoryEvent,
)
from app.errors.common_errors import ValidationError


class ValidateProductCategoryProcessor(BaseProcessor[Product]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_CREATE, RepositoryEvent.PRE_UPDATE]

    async def process(self, context: EntityContext[Product]) -> None:
        product = context.entity
        if not product.product_category_id:
            return

        category = await self._get_category(product.product_category_id)
        if not category:
            raise ValidationError(
                f"Product category with ID '{product.product_category_id}' not found"
            )

        if category.factory_id and category.factory_id != product.factory_id:
            raise ValidationError(
                f"Product factory '{product.factory_id}' does not match "
                f"category factory '{category.factory_id}'"
            )

    async def _get_category(self, category_id: UUID) -> ProductCategory | None:
        stmt = select(ProductCategory).where(ProductCategory.id == category_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
