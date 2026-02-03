import strawberry
from aioinject import Injected
from commons.graphql.filter_types import Filter
from commons.graphql.order_by_types import OrderBy

from app.graphql.common.landing_source_type import LandingSourceType
from app.graphql.common.paginated_landing_page import PaginatedLandingPageInterface
from app.graphql.common.services.landing_page_service import LandingPageService
from app.graphql.inject import inject


@strawberry.type
class LandingPageQueries:
    """Generic GraphQL queries for landing pages across all entity types."""

    @strawberry.field
    @inject
    async def find_landing_pages(
        self,
        service: Injected[LandingPageService],
        source_type: LandingSourceType,
        filters: list[strawberry.input(Filter)] | None = None,
        order_by: list[strawberry.input(OrderBy)] | None = None,
        limit: int | None = 10,
        offset: int | None = 0,
    ) -> PaginatedLandingPageInterface:
        """
        Find landing pages for any entity type with pagination and filtering.

        Args:
            service: Landing page service instance
            source_type: The entity type to query (jobs, companies, contacts, tasks)
            filters: Optional list of filters to apply
            order_by: Optional list of order by clauses
            limit: Maximum number of records to return (default: 10)
            offset: Number of records to skip (default: 0)

        Returns:
            Paginated landing page response for the specified entity type
        """
        return await service.find_landing_pages(
            source_type=source_type,
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset,
        )
