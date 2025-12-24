import strawberry
from aioinject import Injected

from app.graphql.common.services.universal_search_service import UniversalSearchService
from app.graphql.common.strawberry.search_types import SearchResultGQL
from app.graphql.inject import inject


@strawberry.type
class UniversalSearchQueries:
    @strawberry.field
    @inject
    async def universal_search(
        self,
        search_term: str,
        service: Injected[UniversalSearchService],
        limit: int = 20,
    ) -> list[SearchResultGQL]:
        return await service.search(search_term, limit)
