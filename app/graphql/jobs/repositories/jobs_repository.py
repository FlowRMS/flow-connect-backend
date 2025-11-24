"""Repository for Jobs entity with specific database operations."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.base_repository import BaseRepository
from app.graphql.jobs.models.jobs_model import Job


class JobsRepository(BaseRepository[Job]):
    """
    Repository for Jobs entity.

    Extends BaseRepository with job-specific query methods.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the Jobs repository.

        Args:
            session: SQLAlchemy async session
        """
        super().__init__(session, Job)
