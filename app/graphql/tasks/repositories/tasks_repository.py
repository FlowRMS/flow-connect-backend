from typing import Any

from commons.db.models.user import User
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, lazyload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.tasks.models.task_model import Task
from app.graphql.tasks.strawberry.task_landing_page_response import (
    TaskLandingPageResponse,
)


class TasksRepository(BaseRepository[Task]):
    """Repository for Tasks entity."""

    landing_model = TaskLandingPageResponse

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, Task)

    def paginated_stmt(self) -> Select[Any]:
        """
        Build paginated query for tasks landing page.

        Returns:
            SQLAlchemy select statement with columns for landing page
        """
        assigned_to_alias = aliased(User)
        return (
            select(
                Task.id,
                Task.created_at,
                User.full_name.label("created_by"),
                Task.title,
                Task.status,
                Task.priority,
                Task.description,
                assigned_to_alias.full_name.label("assigned_to"),
                Task.due_date,
            )
            .select_from(Task)
            .options(lazyload("*"))
            .join(User, User.id == Task.created_by)
            .outerjoin(assigned_to_alias, assigned_to_alias.id == Task.assigned_to_id)
        )
