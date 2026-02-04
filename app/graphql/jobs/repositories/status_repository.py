from commons.db.v6.crm.jobs.job_status_model import JobStatus
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class JobStatusRepository(BaseRepository[JobStatus]):
    """
    Repository for JobStatus entity.

    Extends BaseRepository with job status-specific query methods.
    """

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        """
        Initialize the JobStatus repository.

        Args:
            context_wrapper: Context wrapper for accessing auth info
            session: SQLAlchemy async session
        """
        super().__init__(session, context_wrapper, JobStatus)
