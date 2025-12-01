from uuid import UUID

from commons.auth import AuthInfo

from app.errors.common_errors import NotFoundError
from app.graphql.links.models.entity_type import EntityType
from app.graphql.tasks.models.task_conversation_model import TaskConversation
from app.graphql.tasks.models.task_model import Task
from app.graphql.tasks.repositories.task_conversations_repository import (
    TaskConversationsRepository,
)
from app.graphql.tasks.repositories.tasks_repository import TasksRepository
from app.graphql.tasks.strawberry.task_conversation_input import TaskConversationInput
from app.graphql.tasks.strawberry.task_input import TaskInput


class TasksService:
    """Service for Tasks entity business logic."""

    def __init__(
        self,
        repository: TasksRepository,
        conversations_repository: TaskConversationsRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.conversations_repository = conversations_repository
        self.auth_info = auth_info

    async def create_task(self, task_input: TaskInput) -> Task:
        """Create a new task."""
        task = task_input.to_orm_model()
        return await self.repository.create(task)

    async def update_task(self, task_id: UUID, task_input: TaskInput) -> Task:
        """Update an existing task."""
        if not await self.repository.exists(task_id):
            raise NotFoundError(str(task_id))

        task = task_input.to_orm_model()
        task.id = task_id
        return await self.repository.update(task)

    async def delete_task(self, task_id: UUID | str) -> bool:
        """Delete a task by ID."""
        if not await self.repository.exists(task_id):
            raise NotFoundError(str(task_id))
        return await self.repository.delete(task_id)

    async def get_task(self, task_id: UUID | str) -> Task:
        """Get a task by ID."""
        task = await self.repository.get_by_id(task_id)
        if not task:
            raise NotFoundError(str(task_id))
        return task

    async def add_conversation(
        self, conversation_input: TaskConversationInput
    ) -> TaskConversation:
        """Add a conversation entry to a task."""
        if not await self.repository.exists(conversation_input.task_id):
            raise NotFoundError(str(conversation_input.task_id))
        return await self.conversations_repository.create(
            conversation_input.to_orm_model()
        )

    async def update_conversation(
        self, conversation_id: UUID, conversation_input: TaskConversationInput
    ) -> TaskConversation:
        """Update an existing conversation entry."""
        if not await self.conversations_repository.exists(conversation_id):
            raise NotFoundError(str(conversation_id))
        conversation = conversation_input.to_orm_model()
        conversation.id = conversation_id
        return await self.conversations_repository.update(conversation)

    async def delete_conversation(self, conversation_id: UUID | str) -> bool:
        """Delete a conversation entry by ID."""
        if not await self.conversations_repository.exists(conversation_id):
            raise NotFoundError(str(conversation_id))
        return await self.conversations_repository.delete(conversation_id)

    async def get_conversations_by_task(self, task_id: UUID) -> list[TaskConversation]:
        """Get all conversation entries for a specific task."""
        if not await self.repository.exists(task_id):
            raise NotFoundError(str(task_id))
        return await self.conversations_repository.get_by_task_id(task_id)

    async def search_tasks(self, search_term: str, limit: int = 20) -> list[Task]:
        """
        Search tasks by title.

        Args:
            search_term: The search term to match against task title
            limit: Maximum number of tasks to return (default: 20)

        Returns:
            List of Task objects matching the search criteria
        """
        return await self.repository.search_by_title(search_term, limit)

    async def find_tasks_by_note_id(self, note_id: UUID) -> list[Task]:
        """Find all tasks linked to the given note ID."""
        return await self.repository.find_by_entity(EntityType.NOTE, note_id)
