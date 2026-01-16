from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.tasks.services.task_categories_service import TaskCategoriesService
from app.graphql.tasks.strawberry.task_category_input import (
    CreateTaskCategoryInput,
    UpdateTaskCategoryInput,
)
from app.graphql.tasks.strawberry.task_category_response import TaskCategoryType


@strawberry.type
class TaskCategoriesMutations:

    @strawberry.mutation
    @inject
    async def create_task_category(
        self,
        input: CreateTaskCategoryInput,
        service: Injected[TaskCategoriesService],
    ) -> TaskCategoryType:
        category = await service.create_category(input)
        return TaskCategoryType.from_orm_model(category)

    @strawberry.mutation
    @inject
    async def update_task_category(
        self,
        id: UUID,
        input: UpdateTaskCategoryInput,
        service: Injected[TaskCategoriesService],
    ) -> TaskCategoryType:
        category = await service.update_category(id, input)
        return TaskCategoryType.from_orm_model(category)

    @strawberry.mutation
    @inject
    async def delete_task_category(
        self,
        id: UUID,
        service: Injected[TaskCategoriesService],
    ) -> bool:
        return await service.delete_category(id)
