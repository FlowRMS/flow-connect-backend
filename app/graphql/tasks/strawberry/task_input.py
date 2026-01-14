from datetime import date
from uuid import UUID

import strawberry
from commons.db.v6.crm.tasks.task_model import Task
from commons.db.v6.crm.tasks.task_priority import TaskPriority
from commons.db.v6.crm.tasks.task_status import TaskStatus

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class TaskInput(BaseInputGQL[Task]):
    title: str
    status: TaskStatus
    priority: TaskPriority
    description: str | None = strawberry.UNSET
    assignee_ids: list[UUID] | None = strawberry.UNSET
    due_date: date | None = strawberry.UNSET
    reminder_date: date | None = strawberry.UNSET
    tags: list[str] | None = strawberry.UNSET

    def to_orm_model(self) -> Task:
        return Task(
            title=self.title,
            status=self.status,
            priority=self.priority,
            description=self.optional_field(self.description),
            due_date=self.optional_field(self.due_date),
            reminder_date=self.optional_field(self.reminder_date),
            tags=self.optional_field(self.tags) or [],
        )

    def get_assignee_ids(self) -> list[UUID]:
        return self.optional_field(self.assignee_ids) or []
