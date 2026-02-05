from typing import Any, override

from commons.db.v6.core.factories.factory import Factory
from sqlalchemy import func
from sqlalchemy.orm import InstrumentedAttribute

from app.graphql.common.builders.search_query_builder import SearchQueryBuilder
from app.graphql.common.interfaces.search_query_interface import SearchQueryStrategy
from app.graphql.common.strawberry.source_type import SourceType


class FactorySearchQueryBuilder(SearchQueryBuilder[Factory]):
    @override
    def get_searchable_fields(
        self,
    ) -> list[InstrumentedAttribute[str] | InstrumentedAttribute[str | None]]:
        return [Factory.title, Factory.account_number, Factory.email, Factory.phone]

    @override
    def get_title_field(self) -> InstrumentedAttribute[str]:
        return Factory.title

    @override
    def get_alias_field(self) -> Any | None:
        return func.coalesce(Factory.account_number, Factory.email, Factory.phone)


class FactorySearchStrategy(SearchQueryStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.query_builder = FactorySearchQueryBuilder(Factory, SourceType.FACTORY)

    @override
    def get_supported_source_type(self) -> SourceType:
        return SourceType.FACTORY

    @override
    def get_model_class(self) -> type[Any]:
        return Factory

    @override
    def build_search_query(self, search_term: str) -> Any:
        return self.query_builder.build_search_query(search_term)
