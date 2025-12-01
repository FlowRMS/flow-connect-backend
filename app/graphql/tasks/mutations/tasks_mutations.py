from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.tasks.services.tasks_service import TasksService
from app.graphql.tasks.strawberry.task_conversation_input import TaskConversationInput
from app.graphql.tasks.strawberry.task_conversation_response import (
    TaskConversationType,
)
from app.graphql.tasks.strawberry.task_input import TaskInput
from app.graphql.tasks.strawberry.task_response import TaskType


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
    async def add_task_conversation(
        self,
        input: TaskConversationInput,
        service: Injected[TasksService],
    ) -> TaskConversationType:
        """Add a conversation entry to a task."""
        return TaskConversationType.from_orm_model(
            await service.add_conversation(conversation_input=input)
        )

    @strawberry.mutation
    @inject
    async def update_task_conversation(
        self,
        id: UUID,
        input: TaskConversationInput,
        service: Injected[TasksService],
    ) -> TaskConversationType:
        """Update an existing conversation entry."""
        return TaskConversationType.from_orm_model(
            await service.update_conversation(
                conversation_id=id, conversation_input=input
            )
        )

    @strawberry.mutation
    @inject
    async def delete_task_conversation(
        self,
        id: UUID,
        service: Injected[TasksService],
    ) -> bool:
        """Delete a conversation entry by ID."""
        return await service.delete_conversation(conversation_id=id)
