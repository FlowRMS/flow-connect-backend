"""GraphQL landing page queries for Jobs entity."""

import strawberry
from aioinject import Injected
from commons.graphql.filter_types import Filter
from commons.graphql.order_by_types import OrderBy

from app.graphql.common.paginated_landing_page import PaginatedLandingPageInterface
from app.graphql.inject import inject
from app.graphql.jobs.services.jobs_landing_service import JobsLandingService


@strawberry.type
class JobsLandingQueries:
    """GraphQL queries for Jobs landing page."""

    @strawberry.field
    @inject
    async def find_jobs(
        self,
        service: Injected[JobsLandingService],
        filters: list[strawberry.input(Filter)] | None = None,
        order_by: list[strawberry.input(OrderBy)] | None = None,
        limit: int | None = 10,
        offset: int | None = 0,
    ) -> PaginatedLandingPageInterface:
        """
        Find jobs with pagination and filtering.

        Args:
            service: Jobs landing service instance
            filters: Optional list of filters to apply
            order_by: Optional list of order by clauses
            limit: Maximum number of records to return (default: 10)
            offset: Number of records to skip (default: 0)

        Returns:
            Paginated landing page response with jobs
        """
        return await service.find_jobs(
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset,
        )
