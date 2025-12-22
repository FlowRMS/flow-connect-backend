from datetime import date, datetime
from uuid import UUID

import strawberry
from commons.db.v6.crm.tasks.task_model import Task
from commons.db.v6.crm.tasks.task_priority import TaskPriority
from commons.db.v6.crm.tasks.task_status import TaskStatus

from app.core.db.adapters.dto import DTOMixin
from app.graphql.users.strawberry.user_response import UserResponse


@strawberry.type
class TaskType(DTOMixin[Task]):
    """GraphQL type for Task entity (output/query results)."""

    _instance: strawberry.Private[Task]
    id: UUID
    created_at: datetime
    title: str
    status: TaskStatus
    priority: TaskPriority
    description: str | None
    assigned_to_id: UUID | None
    due_date: date | None
    reminder_date: date | None
    tags: list[str] | None

    @classmethod
    def from_orm_model(cls, model: Task) -> "TaskType":
        """Convert ORM model to GraphQL type."""
        return cls(
            _instance=model,
            id=model.id,
            created_at=model.created_at,
            title=model.title,
            status=model.status,
            priority=model.priority,
            description=model.description,
            assigned_to_id=model.assigned_to_id,
            due_date=model.due_date,
            reminder_date=model.reminder_date,
            tags=model.tags,
        )

    @strawberry.field
    def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.created_by)
