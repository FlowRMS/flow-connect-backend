"""Landing page service for Jobs entity."""

from commons.db.v6.crm.jobs.jobs_model import Job
from commons.graphql.filter_types import Filter
from commons.graphql.order_by_types import OrderBy

from app.graphql.common.paginated_landing_page import PaginatedLandingPageInterface
from app.graphql.jobs.repositories.jobs_repository import JobsRepository
from app.graphql.jobs.strawberry.job_landing_page_response import (
    JobLandingPageResponse,
)


class JobsLandingService:
    """Service for Jobs landing page queries."""

    def __init__(self, repository: JobsRepository) -> None:
        """
        Initialize the Jobs landing service.

        Args:
            repository: Jobs repository instance
        """
        super().__init__()
        self.repository = repository

    async def find_jobs(
        self,
        filters: list[Filter] | None = None,
        order_by: list[OrderBy] | None = None,
        limit: int | None = 10,
        offset: int | None = 0,
    ) -> PaginatedLandingPageInterface:
        """
        Find jobs with pagination and filtering.

        Args:
            filters: Optional list of filters to apply
            order_by: Optional list of order by clauses
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            Paginated landing page response with jobs
        """
        return await PaginatedLandingPageInterface.get_pagination_window(
            session=self.repository.session,
            stmt=self.repository.paginated_stmt(),
            record_type=Job,
            record_type_gql=JobLandingPageResponse,
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset,
        )
