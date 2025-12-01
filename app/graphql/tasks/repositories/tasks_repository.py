from typing import Any
from uuid import UUID

from commons.db.models.user import User
from sqlalchemy import Select, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, lazyload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.links.models.entity_type import EntityType
from app.graphql.links.models.link_relation_model import LinkRelation
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
                Task.reminder_date,
                Task.tags,
            )
            .select_from(Task)
            .options(lazyload("*"))
            .join(User, User.id == Task.created_by)
            .outerjoin(assigned_to_alias, assigned_to_alias.id == Task.assigned_to_id)
        )

    async def search_by_title(self, search_term: str, limit: int = 20) -> list[Task]:
        """
        Search tasks by title using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against task title
            limit: Maximum number of tasks to return (default: 20)

        Returns:
            List of Task objects matching the search criteria
        """
        stmt = select(Task).where(Task.title.ilike(f"%{search_term}%")).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_entity(
        self,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> list[Task]:
        """Find all tasks linked to a specific entity via link relations."""
        stmt = select(Task).join(
            LinkRelation,
            or_(
                # Tasks as source, entity as target
                (
                    (LinkRelation.source_entity_type == EntityType.TASK)
                    & (LinkRelation.target_entity_type == entity_type)
                    & (LinkRelation.target_entity_id == entity_id)
                    & (LinkRelation.source_entity_id == Task.id)
                ),
                # Entity as source, Tasks as target
                (
                    (LinkRelation.source_entity_type == entity_type)
                    & (LinkRelation.target_entity_type == EntityType.TASK)
                    & (LinkRelation.source_entity_id == entity_id)
                    & (LinkRelation.target_entity_id == Task.id)
                ),
            ),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
