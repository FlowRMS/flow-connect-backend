from uuid import UUID

from commons.db.v6.core.products.product_category import ProductCategory
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.processors import (
    BaseProcessor,
    EntityContext,
    RepositoryEvent,
)
from app.errors.common_errors import ValidationError


class ValidateProductCategoryHierarchyProcessor(BaseProcessor[ProductCategory]):
    """Validate product category hierarchy rules:
    1. Cannot set grandparent without parent
    2. Grandparent must be parent's parent
    3. Maximum depth is 3 levels (cannot create child of Level 3 category)
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_CREATE, RepositoryEvent.PRE_UPDATE]

    async def process(self, context: EntityContext[ProductCategory]) -> None:
        category = context.entity

        # Rule 1: Cannot set grandparent without parent
        if category.grandparent_id and not category.parent_id:
            raise ValidationError("Cannot set grandparent without a parent")

        if category.parent_id:
            parent = await self._get_category(category.parent_id)
            if not parent:
                raise ValidationError(
                    f"Parent category not found: {category.parent_id}"
                )

            # Rule 2: Grandparent must be parent's parent
            if category.grandparent_id:
                if parent.parent_id != category.grandparent_id:
                    raise ValidationError("Grandparent must be the parent's parent")

            # Rule 3: Maximum depth is 3 levels
            # If parent has a grandparent, it's Level 3 - cannot add children
            if parent.grandparent_id is not None:
                raise ValidationError(
                    "Maximum hierarchy depth is 3 levels. "
                    "Cannot create child of a Level 3 category."
                )

    async def _get_category(self, category_id: UUID) -> ProductCategory | None:
        stmt = select(ProductCategory).where(ProductCategory.id == category_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
