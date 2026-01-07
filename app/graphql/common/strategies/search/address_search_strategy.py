from typing import Any, override

from commons.db.v6.core.addresses.address import Address
from sqlalchemy import func
from sqlalchemy.orm import InstrumentedAttribute

from app.graphql.common.builders.search_query_builder import SearchQueryBuilder
from app.graphql.common.interfaces.search_query_interface import SearchQueryStrategy
from app.graphql.common.strawberry.search_types import SourceType


class AddressSearchQueryBuilder(SearchQueryBuilder[Address]):
    @override
    def get_searchable_fields(
        self,
    ) -> list[InstrumentedAttribute[str] | InstrumentedAttribute[str | None]]:
        return [
            Address.line_1,
            Address.line_2,
            Address.city,
            Address.state,
            Address.zip_code,
            Address.country,
        ]

    @override
    def get_title_field(self) -> Any:
        return func.concat(Address.line_1, ", ", Address.city)

    @override
    def get_alias_field(self) -> Any | None:
        return func.coalesce(Address.state, Address.zip_code, Address.country)


class AddressSearchStrategy(SearchQueryStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.query_builder = AddressSearchQueryBuilder(Address, SourceType.ADDRESS)

    @override
    def get_supported_source_type(self) -> SourceType:
        return SourceType.ADDRESS

    @override
    def get_model_class(self) -> type[Any]:
        return Address

    @override
    def build_search_query(self, search_term: str) -> Any:
        return self.query_builder.build_search_query(search_term)
