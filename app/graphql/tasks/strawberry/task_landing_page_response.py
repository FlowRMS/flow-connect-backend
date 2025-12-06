"""Landing page response type for Tasks entity."""

from datetime import date

import strawberry

from app.core.db.adapters.dto import LandingPageInterfaceBase
from app.graphql.tasks.models.task_priority import TaskPriority
from app.graphql.tasks.models.task_status import TaskStatus


@strawberry.type(name="TaskLandingPage")
class TaskLandingPageResponse(LandingPageInterfaceBase):
    """Landing page response for tasks with key fields for list views."""

    title: str
    status: TaskStatus
    priority: TaskPriority
    description: str | None
    assigned_to: str | None
    due_date: date | None
    reminder_date: date | None
    tags: list[str] | None
    linked_titles: list[str]
