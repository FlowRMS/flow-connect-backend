from typing import Any, override

from commons.db.v6.commission.checks import Adjustment
from sqlalchemy.orm import InstrumentedAttribute

from app.graphql.common.builders.search_query_builder import SearchQueryBuilder
from app.graphql.common.interfaces.search_query_interface import SearchQueryStrategy
from app.graphql.common.strawberry.source_type import SourceType


class AdjustmentSearchQueryBuilder(SearchQueryBuilder[Adjustment]):
    @override
    def get_searchable_fields(
        self,
    ) -> list[InstrumentedAttribute[str] | InstrumentedAttribute[str | None]]:
        return [
            Adjustment.adjustment_number,
            Adjustment.reason,
        ]

    @override
    def get_title_field(self) -> Any:
        return Adjustment.adjustment_number

    @override
    def get_alias_field(self) -> Any | None:
        return Adjustment.reason


class AdjustmentSearchStrategy(SearchQueryStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.query_builder = AdjustmentSearchQueryBuilder(
            Adjustment, SourceType.ADJUSTMENT
        )

    @override
    def get_supported_source_type(self) -> SourceType:
        return SourceType.ADJUSTMENT

    @override
    def get_model_class(self) -> type[Any]:
        return Adjustment

    @override
    def build_search_query(self, search_term: str) -> Any:
        return self.query_builder.build_search_query(search_term)
