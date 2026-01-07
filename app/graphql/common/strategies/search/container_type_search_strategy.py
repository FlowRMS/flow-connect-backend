from typing import Any, override

from commons.db.v6.crm.container_types.container_type_model import ContainerType
from sqlalchemy.orm import InstrumentedAttribute

from app.graphql.common.builders.search_query_builder import SearchQueryBuilder
from app.graphql.common.interfaces.search_query_interface import SearchQueryStrategy
from app.graphql.common.strawberry.search_types import SourceType


class ContainerTypeSearchQueryBuilder(SearchQueryBuilder[ContainerType]):
    @override
    def get_searchable_fields(
        self,
    ) -> list[InstrumentedAttribute[str] | InstrumentedAttribute[str | None]]:
        return [ContainerType.name]

    @override
    def get_title_field(self) -> Any:
        return ContainerType.name

    @override
    def get_alias_field(self) -> Any | None:
        return None


class ContainerTypeSearchStrategy(SearchQueryStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.query_builder = ContainerTypeSearchQueryBuilder(
            ContainerType, SourceType.CONTAINER_TYPE
        )

    @override
    def get_supported_source_type(self) -> SourceType:
        return SourceType.CONTAINER_TYPE

    @override
    def get_model_class(self) -> type[Any]:
        return ContainerType

    @override
    def build_search_query(self, search_term: str) -> Any:
        return self.query_builder.build_search_query(search_term)
