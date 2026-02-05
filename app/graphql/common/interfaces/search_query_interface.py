from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import Select

from app.graphql.common.strawberry.source_type import SourceType


class SearchQueryStrategy(ABC):
    @abstractmethod
    def get_supported_source_type(self) -> SourceType:
        pass

    @abstractmethod
    def get_model_class(self) -> type[Any]:
        pass

    @abstractmethod
    def build_search_query(self, search_term: str) -> Select[Any]:
        pass


class SearchQueryStrategyRegistry:
    def __init__(self) -> None:
        super().__init__()
        self._strategies: dict[SourceType, SearchQueryStrategy] = {}

    def register(self, strategy: SearchQueryStrategy) -> None:
        source_type = strategy.get_supported_source_type()
        self._strategies[source_type] = strategy

    def get_by_source_type(self, source_type: SourceType) -> SearchQueryStrategy | None:
        return self._strategies.get(source_type)

    def get_all(self) -> list[SearchQueryStrategy]:
        return list(self._strategies.values())
