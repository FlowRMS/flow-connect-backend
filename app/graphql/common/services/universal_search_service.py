from typing import Any

from sqlalchemy import Result, text, union
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.common.interfaces.search_query_interface import (
    SearchQueryStrategyRegistry,
)
from app.graphql.common.strawberry.search_types import SearchResultGQL


class UniversalSearchService:
    def __init__(
        self,
        session: AsyncSession,
        strategy_registry: SearchQueryStrategyRegistry,
    ) -> None:
        super().__init__()
        self.session = session
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

        result: Result[Any] = await self.session.execute(combined_query)
        return SearchResultGQL.from_row_list(result.fetchall())
