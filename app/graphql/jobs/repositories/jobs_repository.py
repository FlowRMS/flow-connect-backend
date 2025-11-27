"""Repository for Jobs entity with specific database operations."""

from typing import Any

from commons.db.models.user import User
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, lazyload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.jobs.models.jobs_model import Job
from app.graphql.jobs.models.status_model import JobStatus


class JobsRepository(BaseRepository[Job]):
    """
    Repository for Jobs entity.

    Extends BaseRepository with job-specific query methods.
    """

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        """
        Initialize the Jobs repository.

        Args:
            session: SQLAlchemy async session
        """
        super().__init__(session, context_wrapper, Job)

    def paginated_stmt(self) -> Select[Any]:
        """
        Build paginated query for jobs landing page.

        Returns:
            SQLAlchemy select statement with columns for landing page
        """
        user_owner_alias = aliased(User)
        requester_alias = aliased(User)
        return (
            select(
                Job.id,
                Job.created_at,
                User.full_name.label("created_by"),
                Job.job_name,
                JobStatus.name.label("status_name"),
                Job.start_date,
                Job.end_date,
                Job.description,
                Job.job_type,
                requester_alias.full_name.label("requester"),
                user_owner_alias.full_name.label("job_owner"),
            )
            .select_from(Job)
            .options(lazyload("*"))
            .join(JobStatus, JobStatus.id == Job.status_id)
            .join(User, User.id == Job.created_by)
            .outerjoin(user_owner_alias, user_owner_alias.id == Job.job_owner_id)
            .outerjoin(requester_alias, requester_alias.id == Job.requester_id)
        )
