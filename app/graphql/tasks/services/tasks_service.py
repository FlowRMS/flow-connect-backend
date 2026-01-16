from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.tasks.task_assignee_model import TaskAssignee
from commons.db.v6.crm.tasks.task_conversation_model import TaskConversation
from commons.db.v6.crm.tasks.task_model import Task
from sqlalchemy.orm import joinedload, lazyload, selectinload

from app.errors.common_errors import NotFoundError
from app.graphql.tasks.repositories.task_conversations_repository import (
    TaskConversationsRepository,
)
from app.graphql.tasks.repositories.tasks_repository import TasksRepository
from app.graphql.tasks.strawberry.task_conversation_input import TaskConversationInput
from app.graphql.tasks.strawberry.task_input import TaskInput


class TasksService:
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

    async def find_task_by_id(self, task_id: UUID) -> Task:
        task = await self.repository.get_by_id(
            task_id,
            options=[
                joinedload(Task.created_by),
                joinedload(Task.category),
                selectinload(Task.assignees).joinedload(TaskAssignee.user),
                lazyload("*"),
            ],
        )
        if not task:
            raise NotFoundError(str(task_id))
        return task

    async def create_task(self, task_input: TaskInput) -> Task:
        task = task_input.to_orm_model()
        self.repository.sync_assignees_processor.set_assignee_ids(
            task.id, task_input.get_assignee_ids()
        )
        _ = await self.repository.create(task)
        return await self.find_task_by_id(task.id)

    async def update_task(self, task_id: UUID, task_input: TaskInput) -> Task:
        if not await self.repository.exists(task_id):
            raise NotFoundError(str(task_id))

        task = task_input.to_orm_model()
        task.id = task_id
        self.repository.sync_assignees_processor.set_assignee_ids(
            task_id, task_input.get_assignee_ids()
        )
        _ = await self.repository.update(task)
        return await self.find_task_by_id(task_id)

    async def delete_task(self, task_id: UUID | str) -> bool:
        if not await self.repository.exists(task_id):
            raise NotFoundError(str(task_id))
        return await self.repository.delete(task_id)

    async def add_conversation(
        self, conversation_input: TaskConversationInput
    ) -> TaskConversation:
        if not await self.repository.exists(conversation_input.task_id):
            raise NotFoundError(str(conversation_input.task_id))
        task_conversation = await self.conversations_repository.create(
            conversation_input.to_orm_model()
        )
        return await self.conversations_repository.get_by_id(
            task_conversation.id,
            options=[
                joinedload(TaskConversation.created_by),
                lazyload("*"),
            ],
        )

    async def update_conversation(
        self, conversation_id: UUID, conversation_input: TaskConversationInput
    ) -> TaskConversation:
        if not await self.conversations_repository.exists(conversation_id):
            raise NotFoundError(str(conversation_id))
        conversation = conversation_input.to_orm_model()
        conversation.id = conversation_id
        _ = await self.conversations_repository.update(conversation)
        return await self.conversations_repository.get_by_id(
            conversation.id,
            options=[
                joinedload(TaskConversation.created_by),
                lazyload("*"),
            ],
        )

    async def delete_conversation(self, conversation_id: UUID | str) -> bool:
        if not await self.conversations_repository.exists(conversation_id):
            raise NotFoundError(str(conversation_id))
        return await self.conversations_repository.delete(conversation_id)

    async def get_conversations_by_task(self, task_id: UUID) -> list[TaskConversation]:
        if not await self.repository.exists(task_id):
            raise NotFoundError(str(task_id))
        return await self.conversations_repository.get_by_task_id(task_id)

    async def search_tasks(self, search_term: str, limit: int = 20) -> list[Task]:
        return await self.repository.search_by_title(search_term, limit)

    async def find_tasks_by_note_id(self, note_id: UUID) -> list[Task]:
        return await self.repository.find_by_entity(EntityType.NOTE, note_id)

    async def find_tasks_by_entity(
        self, entity_type: EntityType, entity_id: UUID
    ) -> list[Task]:
        return await self.repository.find_by_entity(entity_type, entity_id)
