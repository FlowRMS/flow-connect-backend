from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.tasks.services.tasks_service import TasksService
from app.graphql.tasks.strawberry.task_response import TaskType


@strawberry.type
class TasksQueries:
    """GraphQL queries for Tasks entity."""

    @strawberry.field
    @inject
    async def task(
        self,
        id: UUID,
        service: Injected[TasksService],
    ) -> TaskType:
        """Get a task by ID."""
        return TaskType.from_orm_model(await service.get_task(id))
