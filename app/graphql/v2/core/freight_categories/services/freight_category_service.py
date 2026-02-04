from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.warehouse import FreightCategory

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.freight_categories.repositories import (
    FreightCategoriesRepository,
)
from app.graphql.v2.core.freight_categories.strawberry.freight_category_input import (
    FreightCategoryInput,
)


class FreightCategoryService:
    def __init__(
        self,
        repository: FreightCategoriesRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_by_id(self, freight_category_id: UUID) -> FreightCategory:
        freight_category = await self.repository.get_by_id(freight_category_id)
        if not freight_category:
            raise NotFoundError(
                f"Freight category with id {freight_category_id} not found"
            )
        return freight_category

    async def list_all(self) -> list[FreightCategory]:
        return await self.repository.list_all_ordered()

    async def list_active(self) -> list[FreightCategory]:
        return await self.repository.list_active_ordered()

    async def create(self, input: FreightCategoryInput) -> FreightCategory:
        freight_category = input.to_orm_model()

        # Auto-assign position if not provided
        if freight_category.position == 0:
            max_position = await self.repository.get_max_position()
            freight_category.position = max_position + 1

        return await self.repository.create(freight_category)

    async def update(
        self, freight_category_id: UUID, input: FreightCategoryInput
    ) -> FreightCategory:
        existing = await self.repository.get_by_id(freight_category_id)
        if not existing:
            raise NotFoundError(
                f"Freight category with id {freight_category_id} not found"
            )

        freight_category = input.to_orm_model()
        freight_category.id = freight_category_id

        # Keep existing position if not provided
        if freight_category.position == 0:
            freight_category.position = existing.position

        return await self.repository.update(freight_category)

    async def delete(self, freight_category_id: UUID) -> bool:
        if not await self.repository.exists(freight_category_id):
            raise NotFoundError(
                f"Freight category with id {freight_category_id} not found"
            )
        return await self.repository.delete(freight_category_id)

    async def reorder(self, ordered_ids: list[UUID]) -> list[FreightCategory]:
        return await self.repository.reorder(ordered_ids)
