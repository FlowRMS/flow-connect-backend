from typing import Any, override

from commons.db.v6.core.factories import Factory
from commons.db.v6.core.products.product import Product
from sqlalchemy.orm import InstrumentedAttribute

from app.graphql.common.builders.search_query_builder import SearchQueryBuilder
from app.graphql.common.interfaces.search_query_interface import SearchQueryStrategy
from app.graphql.common.strawberry.search_types import SourceType


class ProductSearchQueryBuilder(SearchQueryBuilder[Product]):
    @override
    def get_searchable_fields(
        self,
    ) -> list[InstrumentedAttribute[str] | InstrumentedAttribute[str | None]]:
        return [Product.factory_part_number, Product.description]

    @override
    def get_title_field(self) -> InstrumentedAttribute[str]:
        return Product.factory_part_number

    @override
    def get_alias_field(self) -> Any | None:
        return Product.description

    @override
    def get_extra_info_field(self) -> Any | None:
        return Factory.title

    @override
    def get_joins(self) -> list[tuple[Any, Any]]:
        return [(Factory, Product.factory_id == Factory.id)]


class ProductSearchStrategy(SearchQueryStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.query_builder = ProductSearchQueryBuilder(Product, SourceType.PRODUCT)

    @override
    def get_supported_source_type(self) -> SourceType:
        return SourceType.PRODUCT

    @override
    def get_model_class(self) -> type[Any]:
        return Product

    @override
    def build_search_query(self, search_term: str) -> Any:
        return self.query_builder.build_search_query(search_term)
