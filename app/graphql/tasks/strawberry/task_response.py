from datetime import date, datetime
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.tasks.models.task_model import Task
from app.graphql.tasks.models.task_priority import TaskPriority
from app.graphql.tasks.models.task_status import TaskStatus


@strawberry.type
class TaskType(DTOMixin[Task]):
    """GraphQL type for Task entity (output/query results)."""

    id: UUID
    created_at: datetime
    created_by: UUID
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
            id=model.id,
            created_at=model.created_at,
            created_by=model.created_by,
            title=model.title,
            status=model.status,
            priority=model.priority,
            description=model.description,
            assigned_to_id=model.assigned_to_id,
            due_date=model.due_date,
            reminder_date=model.reminder_date,
            tags=model.tags,
        )
