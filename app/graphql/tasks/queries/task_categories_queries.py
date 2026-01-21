from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.tasks.services.task_categories_service import TaskCategoriesService
from app.graphql.tasks.strawberry.task_category_response import TaskCategoryType


@strawberry.type
class TaskCategoriesQueries:
    @strawberry.field
    @inject
    async def task_categories(
        self,
        service: Injected[TaskCategoriesService],
        include_inactive: bool = False,
    ) -> list[TaskCategoryType]:
        categories = await service.list_categories(include_inactive=include_inactive)
        return TaskCategoryType.from_orm_model_list(categories)

    @strawberry.field
    @inject
    async def task_category(
        self,
        id: UUID,
        service: Injected[TaskCategoriesService],
    ) -> TaskCategoryType:
        category = await service.get_category_by_id(id)
        return TaskCategoryType.from_orm_model(category)
