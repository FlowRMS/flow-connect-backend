from typing import Any, override

from commons.db.v6.commission.checks import Check
from commons.db.v6.core.factories import Factory
from sqlalchemy.orm import InstrumentedAttribute

from app.graphql.common.builders.search_query_builder import SearchQueryBuilder
from app.graphql.common.interfaces.search_query_interface import SearchQueryStrategy
from app.graphql.common.strawberry.source_type import SourceType


class CheckSearchQueryBuilder(SearchQueryBuilder[Check]):
    @override
    def get_searchable_fields(
        self,
    ) -> list[InstrumentedAttribute[str] | InstrumentedAttribute[str | None]]:
        return [Check.check_number]

    @override
    def get_title_field(self) -> Any:
        return Check.check_number

    @override
    def get_alias_field(self) -> Any | None:
        return None

    @override
    def get_extra_info_field(self) -> Any | None:
        return Factory.title

    @override
    def get_joins(self) -> list[tuple[Any, Any]]:
        return [(Factory, Check.factory_id == Factory.id)]


class CheckSearchStrategy(SearchQueryStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.query_builder = CheckSearchQueryBuilder(Check, SourceType.CHECK)

    @override
    def get_supported_source_type(self) -> SourceType:
        return SourceType.CHECK

    @override
    def get_model_class(self) -> type[Any]:
        return Check

    @override
    def build_search_query(self, search_term: str) -> Any:
        return self.query_builder.build_search_query(search_term)
