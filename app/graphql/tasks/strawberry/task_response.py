from datetime import date, datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.tasks.task_model import Task
from commons.db.v6.crm.tasks.task_priority import TaskPriority
from commons.db.v6.crm.tasks.task_status import TaskStatus

from aioinject import Injected
from commons.db.v6.crm.links.entity_type import EntityType

from app.core.db.adapters.dto import DTOMixin
from app.graphql.inject import inject
from app.graphql.tasks.strawberry.task_category_response import TaskCategoryType
from app.graphql.v2.core.users.strawberry.user_response import UserResponse
from app.graphql.watchers.services.entity_watcher_service import EntityWatcherService


@strawberry.type
class TaskLiteType(DTOMixin[Task]):
    _instance: strawberry.Private[Task]
    id: UUID
    created_at: datetime
    title: str
    status: TaskStatus
    priority: TaskPriority
    description: str | None
    due_date: date | None
    reminder_date: date | None
    tags: list[str] | None
    category_id: UUID | None

    @classmethod
    def from_orm_model(cls, model: Task) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            created_at=model.created_at,
            title=model.title,
            status=model.status,
            priority=model.priority,
            description=model.description,
            due_date=model.due_date,
            reminder_date=model.reminder_date,
            tags=model.tags,
            category_id=model.category_id,
        )


@strawberry.type
class TaskType(TaskLiteType):
    @strawberry.field
    def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.created_by)

    @strawberry.field
    def assignees(self) -> list[UserResponse]:
        return [UserResponse.from_orm_model(ta.user) for ta in self._instance.assignees]

    @strawberry.field
    def category(
        self,
    ) -> TaskCategoryType | None:
        return TaskCategoryType.from_orm_model_optional(self._instance.category)

    @strawberry.field
    @inject
    async def watchers(
        self,
        watcher_service: Injected[EntityWatcherService],
    ) -> list[UserResponse]:
        users = await watcher_service.get_watchers(EntityType.TASK, self.id)
        return [UserResponse.from_orm_model(u) for u in users]
