from uuid import UUID

from commons.db.v6.core.products.product_category import ProductCategory

from app.errors.common_errors import NameAlreadyExistsError, NotFoundError
from app.graphql.v2.core.products.repositories.product_category_repository import (
    ProductCategoryRepository,
)
from app.graphql.v2.core.products.strawberry.product_category_input import (
    ProductCategoryInput,
)


class ProductCategoryService:
    def __init__(self, repository: ProductCategoryRepository) -> None:
        super().__init__()
        self.repository = repository

    async def get_by_id(self, category_id: UUID) -> ProductCategory:
        category = await self.repository.get_by_id(category_id)
        if not category:
            raise NotFoundError(f"ProductCategory with id {category_id} not found")
        return category

    async def list_all(self) -> list[ProductCategory]:
        return await self.repository.list_all()

    async def get_by_factory_id(self, factory_id: UUID) -> list[ProductCategory]:
        return await self.repository.get_by_factory_id(factory_id)

    async def list_with_filters(
        self,
        factory_id: UUID | None = None,
        parent_id: UUID | None = None,
        grandparent_id: UUID | None = None,
    ) -> list[ProductCategory]:
        return await self.repository.list_with_filters(
            factory_id=factory_id,
            parent_id=parent_id,
            grandparent_id=grandparent_id,
        )

    async def get_children(self, parent_id: UUID) -> list[ProductCategory]:
        """Get all categories that have this category as their parent."""
        return await self.repository.get_children(parent_id)

    async def get_root_categories(
        self, factory_id: UUID | None = None
    ) -> list[ProductCategory]:
        """Get all categories with no parent (Level 1 / root categories)."""
        return await self.repository.get_root_categories(factory_id)

    async def _validate_hierarchy(self, category_input: ProductCategoryInput) -> None:
        """Validate hierarchy rules:
        1. Cannot set grandparent without parent
        2. Grandparent must be parent's parent
        3. Maximum depth is 3 levels (cannot create child of Level 3 category)
        """
        if category_input.grandparent_id and not category_input.parent_id:
            raise ValueError("Cannot set grandparent without a parent")

        if category_input.parent_id:
            parent = await self.repository.get_by_id(category_input.parent_id)
            if not parent:
                raise ValueError(f"Parent category not found: {category_input.parent_id}")

            # Validate grandparent consistency
            if category_input.grandparent_id:
                if parent.parent_id != category_input.grandparent_id:
                    raise ValueError("Grandparent must be the parent's parent")

            # Validate maximum depth of 3 levels
            # If parent has a grandparent, it's Level 3 - cannot add children
            if parent.grandparent_id is not None:
                raise ValueError(
                    "Maximum hierarchy depth is 3 levels. "
                    "Cannot create child of a Level 3 category."
                )

    async def create(self, category_input: ProductCategoryInput) -> ProductCategory:
        if await self.repository.name_exists(
            category_input.factory_id, category_input.title
        ):
            raise NameAlreadyExistsError(category_input.title)

        await self._validate_hierarchy(category_input)

        return await self.repository.create(category_input.to_orm_model())

    async def update(
        self, category_id: UUID, category_input: ProductCategoryInput
    ) -> ProductCategory:
        await self._validate_hierarchy(category_input)
        category = category_input.to_orm_model()
        category.id = category_id
        return await self.repository.update(category)

    async def delete(self, category_id: UUID) -> bool:
        if not await self.repository.exists(category_id):
            raise NotFoundError(f"ProductCategory with id {category_id} not found")
        return await self.repository.delete(category_id)
