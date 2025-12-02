import strawberry
from aioinject import Injected

from app.graphql.checks.services.check_service import CheckService
from app.graphql.checks.strawberry.check_response import CheckResponse
from app.graphql.inject import inject


@strawberry.type
class ChecksQueries:
    """GraphQL queries for Checks entity."""

    @strawberry.field
    @inject
    async def check_search(
        self,
        service: Injected[CheckService],
        search_term: str,
        limit: int = 20,
    ) -> list[CheckResponse]:
        """
        Search checks by check number.

        Args:
            search_term: The search term to match against check number
            limit: Maximum number of checks to return (default: 20)

        Returns:
            List of CheckResponse objects matching the search criteria
        """
        return CheckResponse.from_orm_model_list(
            await service.search_checks(search_term, limit)
        )
