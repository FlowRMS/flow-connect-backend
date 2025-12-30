from typing import Any, override

from commons.db.v6.commission.orders import Order
from sqlalchemy import func
from sqlalchemy.orm import InstrumentedAttribute

from app.graphql.common.builders.search_query_builder import SearchQueryBuilder
from app.graphql.common.interfaces.search_query_interface import SearchQueryStrategy
from app.graphql.common.strawberry.search_types import SourceType


class OrderSearchQueryBuilder(SearchQueryBuilder[Order]):
    @override
    def get_searchable_fields(
        self,
    ) -> list[InstrumentedAttribute[str] | InstrumentedAttribute[str | None]]:
        return [
            Order.order_number,
            Order.fact_so_number,
            Order.mark_number,
        ]

    @override
    def get_title_field(self) -> Any:
        return Order.order_number

    @override
    def get_alias_field(self) -> Any | None:
        return func.coalesce(Order.fact_so_number, Order.mark_number)


class OrderSearchStrategy(SearchQueryStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.query_builder = OrderSearchQueryBuilder(Order, SourceType.ORDER)

    @override
    def get_supported_source_type(self) -> SourceType:
        return SourceType.ORDER

    @override
    def get_model_class(self) -> type[Any]:
        return Order

    @override
    def build_search_query(self, search_term: str) -> Any:
        return self.query_builder.build_search_query(search_term)
