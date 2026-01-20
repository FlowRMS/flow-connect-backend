from uuid import UUID

from commons.db.v6.crm.tasks import TaskCategory

from app.errors.common_errors import NotFoundError
from app.graphql.tasks.repositories.task_categories_repository import (
    TaskCategoriesRepository,
)
from app.graphql.tasks.strawberry.task_category_input import (
    TaskCategoryInput,
)


class TaskCategoriesService:
    def __init__(self, repository: TaskCategoriesRepository) -> None:
        super().__init__()
        self.repository = repository

    async def list_categories(
        self, include_inactive: bool = False
    ) -> list[TaskCategory]:
        if include_inactive:
            return await self.repository.list_all_ordered()
        return await self.repository.list_active()

    async def get_category_by_id(self, category_id: UUID) -> TaskCategory:
        category = await self.repository.get_by_id(category_id)
        if not category:
            raise NotFoundError(str(category_id))
        return category

    async def create_category(self, input: TaskCategoryInput) -> TaskCategory:
        category = input.to_orm_model()
        return await self.repository.create(category)

    async def update_category(
        self, category_id: UUID, input: TaskCategoryInput
    ) -> TaskCategory:
        existing = await self.repository.get_by_id(category_id)
        if not existing:
            raise NotFoundError(str(category_id))

        category = input.to_orm_model()
        category.id = category_id
        return await self.repository.update(category)

    async def delete_category(self, category_id: UUID) -> bool:
        existing = await self.repository.get_by_id(category_id)
        if not existing:
            raise NotFoundError(str(category_id))

        # Soft delete by setting is_active to False
        existing.is_active = False
        _ = await self.repository.update(existing)
        return True
