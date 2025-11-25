"""Repository for Jobs entity with specific database operations."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.jobs.models.jobs_model import Job


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
