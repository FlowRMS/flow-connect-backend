"""Generic landing page service that routes to entity-specific repositories."""

from commons.graphql.filter_types import Filter
from commons.graphql.order_by_types import OrderBy

from app.graphql.common.landing_repository_protocol import LandingRepositoryProtocol
from app.graphql.common.landing_source_type import LandingSourceType
from app.graphql.common.paginated_landing_page import PaginatedLandingPageInterface
from app.graphql.jobs.repositories.jobs_repository import JobsRepository


class LandingPageService:
    """Generic service for landing page queries across all entity types."""

    def __init__(
        self,
        jobs_repository: JobsRepository,
        # companies_repository: CompaniesRepository,  # TODO: Add when implemented
        # contacts_repository: ContactsRepository,    # TODO: Add when implemented
        # tasks_repository: TasksRepository,          # TODO: Add when implemented
    ) -> None:
        """
        Initialize the generic landing page service.

        Args:
            jobs_repository: Jobs repository instance
        """
        super().__init__()
        self._repository_map: dict[LandingSourceType, LandingRepositoryProtocol] = {
            LandingSourceType.JOBS: jobs_repository,
            # LandingSourceType.COMPANIES: companies_repository,  # TODO: Add when implemented
            # LandingSourceType.CONTACTS: contacts_repository,    # TODO: Add when implemented
            # LandingSourceType.TASKS: tasks_repository,          # TODO: Add when implemented
        }

    async def find_landing_pages(
        self,
        source_type: LandingSourceType,
        filters: list[Filter] | None = None,
        order_by: list[OrderBy] | None = None,
        limit: int | None = 10,
        offset: int | None = 0,
    ) -> PaginatedLandingPageInterface:
        """
        Find landing pages for any entity type with pagination and filtering.

        Args:
            source_type: The entity type to query
            filters: Optional list of filters to apply
            order_by: Optional list of order by clauses
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            Paginated landing page response

        Raises:
            NotImplementedError: If the source_type is not yet implemented
            ValueError: If the source_type is unknown
        """
        repository = self._repository_map.get(source_type)

        if repository is None:
            raise NotImplementedError(
                f"{source_type.value.title()} landing page not yet implemented"
            )

        return await PaginatedLandingPageInterface.get_pagination_window(
            session=repository.session,
            stmt=repository.paginated_stmt(),
            record_type=repository.model_class,
            record_type_gql=repository.landing_model,
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset,
        )
