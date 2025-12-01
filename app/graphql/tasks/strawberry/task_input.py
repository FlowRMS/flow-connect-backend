from datetime import date
from uuid import UUID

import strawberry

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.tasks.models.task_model import Task
from app.graphql.tasks.models.task_priority import TaskPriority
from app.graphql.tasks.models.task_status import TaskStatus


@strawberry.input
class TaskInput(BaseInputGQL[Task]):
    """GraphQL input type for creating/updating tasks."""

    title: str
    status: TaskStatus
    priority: TaskPriority
    description: str | None = strawberry.UNSET
    assigned_to_id: UUID | None = strawberry.UNSET
    due_date: date | None = strawberry.UNSET
    tags: list[str] | None = strawberry.UNSET

    def to_orm_model(self) -> Task:
        """Convert input to ORM model."""
        return Task(
            title=self.title,
            status=self.status,
            priority=self.priority,
            description=self.optional_field(self.description),
            assigned_to_id=self.optional_field(self.assigned_to_id),
            due_date=self.optional_field(self.due_date),
            tags=self.optional_field(self.tags),
        )
