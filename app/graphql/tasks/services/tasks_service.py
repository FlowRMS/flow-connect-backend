from uuid import UUID

from commons.auth import AuthInfo

from app.errors.common_errors import NotFoundError
from app.graphql.tasks.models.related_entity_type import RelatedEntityType
from app.graphql.tasks.models.task_model import Task
from app.graphql.tasks.models.task_relation_model import TaskRelation
from app.graphql.tasks.repositories.task_relations_repository import (
    TaskRelationsRepository,
)
from app.graphql.tasks.repositories.tasks_repository import TasksRepository
from app.graphql.tasks.strawberry.task_input import TaskInput, TaskRelationInput


class TasksService:
    """Service for Tasks entity business logic."""

    def __init__(
        self,
        repository: TasksRepository,
        relations_repository: TaskRelationsRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.relations_repository = relations_repository
        self.auth_info = auth_info

    async def create_task(self, task_input: TaskInput) -> Task:
        """Create a new task."""
        task = task_input.to_orm_model()
        return await self.repository.create(task)

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

    async def add_task_relation(
        self, task_id: UUID, related_type: RelatedEntityType, related_id: UUID
    ) -> TaskRelation:
        """Add a relation to a task."""
        if not await self.repository.exists(task_id):
            raise NotFoundError(str(task_id))

        relation = TaskRelation(
            task_id=task_id,
            related_type=related_type,
            related_id=related_id,
        )
        return await self.relations_repository.create(relation)

    async def add_task_relation_from_input(
        self, relation_input: TaskRelationInput
    ) -> TaskRelation:
        """Add a relation to a task from input."""
        return await self.add_task_relation(
            task_id=relation_input.task_id,
            related_type=relation_input.related_type,
            related_id=relation_input.related_id,
        )
