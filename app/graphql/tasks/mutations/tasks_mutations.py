from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.tasks.services.tasks_service import TasksService
from app.graphql.tasks.strawberry.task_input import TaskInput, TaskRelationInput
from app.graphql.tasks.strawberry.task_response import TaskRelationType, TaskType


@strawberry.type
class TasksMutations:
    """GraphQL mutations for Tasks entity."""

    @strawberry.mutation
    @inject
    async def create_task(
        self,
        input: TaskInput,
        service: Injected[TasksService],
    ) -> TaskType:
        """Create a new task."""
        return TaskType.from_orm_model(await service.create_task(task_input=input))

    @strawberry.mutation
    @inject
    async def update_task(
        self,
        id: UUID,
        input: TaskInput,
        service: Injected[TasksService],
    ) -> TaskType:
        """Update an existing task."""
        return TaskType.from_orm_model(await service.update_task(id, input))

    @strawberry.mutation
    @inject
    async def delete_task(
        self,
        id: UUID,
        service: Injected[TasksService],
    ) -> bool:
        """Delete a task by ID."""
        return await service.delete_task(task_id=id)

    @strawberry.mutation
    @inject
    async def add_task_relation(
        self,
        input: TaskRelationInput,
        service: Injected[TasksService],
    ) -> TaskRelationType:
        """Add a relation to a task."""
        return TaskRelationType.from_orm_model(
            await service.add_task_relation_from_input(relation_input=input)
        )
