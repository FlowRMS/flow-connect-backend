from typing import Any, override

from commons.db.v6.crm.shipping_carriers.shipping_carrier_model import ShippingCarrier
from sqlalchemy import func
from sqlalchemy.orm import InstrumentedAttribute

from app.graphql.common.builders.search_query_builder import SearchQueryBuilder
from app.graphql.common.interfaces.search_query_interface import SearchQueryStrategy
from app.graphql.common.strawberry.search_types import SourceType


class ShippingCarrierSearchQueryBuilder(SearchQueryBuilder[ShippingCarrier]):
    @override
    def get_searchable_fields(
        self,
    ) -> list[InstrumentedAttribute[str] | InstrumentedAttribute[str | None]]:
        return [
            ShippingCarrier.name,
            ShippingCarrier.code,
            ShippingCarrier.account_number,
        ]

    @override
    def get_title_field(self) -> Any:
        return ShippingCarrier.name

    @override
    def get_alias_field(self) -> Any | None:
        return func.coalesce(ShippingCarrier.code, ShippingCarrier.account_number)


class ShippingCarrierSearchStrategy(SearchQueryStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.query_builder = ShippingCarrierSearchQueryBuilder(
            ShippingCarrier, SourceType.SHIPPING_CARRIER
        )

    @override
    def get_supported_source_type(self) -> SourceType:
        return SourceType.SHIPPING_CARRIER

    @override
    def get_model_class(self) -> type[Any]:
        return ShippingCarrier

    @override
    def build_search_query(self, search_term: str) -> Any:
        return self.query_builder.build_search_query(search_term)
