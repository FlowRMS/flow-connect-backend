from typing import Any, override

from commons.db.v6.warehouse.warehouse_model import Warehouse
from sqlalchemy.orm import InstrumentedAttribute

from app.graphql.common.builders.search_query_builder import SearchQueryBuilder
from app.graphql.common.interfaces.search_query_interface import SearchQueryStrategy
from app.graphql.common.strawberry.source_type import SourceType


class WarehouseSearchQueryBuilder(SearchQueryBuilder[Warehouse]):
    @override
    def get_searchable_fields(
        self,
    ) -> list[InstrumentedAttribute[str] | InstrumentedAttribute[str | None]]:
        return [
            Warehouse.name,
            Warehouse.description,
        ]

    @override
    def get_title_field(self) -> Any:
        return Warehouse.name

    @override
    def get_alias_field(self) -> Any | None:
        return Warehouse.description


class WarehouseSearchStrategy(SearchQueryStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.query_builder = WarehouseSearchQueryBuilder(
            Warehouse, SourceType.WAREHOUSE
        )

    @override
    def get_supported_source_type(self) -> SourceType:
        return SourceType.WAREHOUSE

    @override
    def get_model_class(self) -> type[Any]:
        return Warehouse

    @override
    def build_search_query(self, search_term: str) -> Any:
        return self.query_builder.build_search_query(search_term)
