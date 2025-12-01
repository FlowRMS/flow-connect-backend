from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.tasks.services.tasks_service import TasksService
from app.graphql.tasks.strawberry.task_conversation_response import (
    TaskConversationType,
)
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

    @strawberry.field
    @inject
    async def task_conversations(
        self,
        task_id: UUID,
        service: Injected[TasksService],
    ) -> list[TaskConversationType]:
        """Get all conversation entries for a specific task."""
        conversations = await service.get_conversations_by_task(task_id)
        return [
            TaskConversationType.from_orm_model(conversation)
            for conversation in conversations
        ]
