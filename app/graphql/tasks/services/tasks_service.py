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
                selectinload(Task.assignees).joinedload(TaskAssignee.user),
                lazyload("*"),
            ],
        )
        if not task:
            raise NotFoundError(str(task_id))
        return task

    async def _sync_assignees(self, task: Task, assignee_ids: list[UUID]) -> None:
        current_ids = {ta.user_id for ta in task.assignees}
        new_ids = set(assignee_ids)

        # Remove assignees no longer in list
        for ta in list(task.assignees):
            if ta.user_id not in new_ids:
                task.assignees.remove(ta)

        # Add new assignees
        for user_id in new_ids - current_ids:
            task.assignees.append(TaskAssignee(task_id=task.id, user_id=user_id))

    async def create_task(self, task_input: TaskInput) -> Task:
        task = task_input.to_orm_model()
        created = await self.repository.create(task)

        # Add assignees
        assignee_ids = task_input.get_assignee_ids()
        if assignee_ids:
            for user_id in assignee_ids:
                created.assignees.append(
                    TaskAssignee(task_id=created.id, user_id=user_id)
                )
            await self.repository.session.flush()

        return await self.find_task_by_id(created.id)

    async def update_task(self, task_id: UUID, task_input: TaskInput) -> Task:
        task = await self.repository.get_by_id(
            task_id,
            options=[selectinload(Task.assignees)],
        )
        if not task:
            raise NotFoundError(str(task_id))

        updated_task = task_input.to_orm_model()
        updated_task.id = task_id
        _ = await self.repository.update(updated_task)

        # Sync assignees
        task = await self.repository.get_by_id(
            task_id,
            options=[selectinload(Task.assignees)],
        )
        if task:
            await self._sync_assignees(task, task_input.get_assignee_ids())
            await self.repository.session.flush()

        return await self.find_task_by_id(task_id)

    async def delete_task(self, task_id: UUID | str) -> bool:
        if not await self.repository.exists(task_id):
            raise NotFoundError(str(task_id))
        return await self.repository.delete(task_id)

    async def get_task(self, task_id: UUID | str) -> Task:
        task = await self.repository.get_by_id(task_id)
        if not task:
            raise NotFoundError(str(task_id))
        return task

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
