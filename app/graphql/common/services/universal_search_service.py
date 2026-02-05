from sqlalchemy import text, union

from app.graphql.common.interfaces.search_query_interface import (
    SearchQueryStrategyRegistry,
)
from app.graphql.common.repositories.universal_search_repository import (
    UniversalSearchRepository,
)
from app.graphql.common.strawberry.search_result_gql import SearchResultGQL


class UniversalSearchService:
    def __init__(
        self,
        repository: UniversalSearchRepository,
        strategy_registry: SearchQueryStrategyRegistry,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.strategy_registry = strategy_registry

    async def search(
        self,
        search_term: str,
        limit: int = 20,
    ) -> list[SearchResultGQL]:
        strategies = self.strategy_registry.get_all()
        if not strategies:
            return []

        strategy_queries = [
            strategy.build_search_query(search_term) for strategy in strategies
        ]

        combined_query = (
            union(*strategy_queries).limit(limit).order_by(text("similarity DESC"))
        )

        rows = await self.repository.execute_search_query(combined_query)
        return SearchResultGQL.from_row_list(rows)
