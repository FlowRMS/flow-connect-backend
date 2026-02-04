from typing import Any, override

from commons.db.v6.core.customers.customer import Customer
from sqlalchemy.orm import InstrumentedAttribute

from app.graphql.common.builders.search_query_builder import SearchQueryBuilder
from app.graphql.common.interfaces.search_query_interface import SearchQueryStrategy
from app.graphql.common.strawberry.source_type import SourceType


class CustomerSearchQueryBuilder(SearchQueryBuilder[Customer]):
    @override
    def get_searchable_fields(
        self,
    ) -> list[InstrumentedAttribute[str] | InstrumentedAttribute[str | None]]:
        return [Customer.company_name]

    @override
    def get_title_field(self) -> InstrumentedAttribute[str]:
        return Customer.company_name


class CustomerSearchStrategy(SearchQueryStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.query_builder = CustomerSearchQueryBuilder(Customer, SourceType.CUSTOMER)

    @override
    def get_supported_source_type(self) -> SourceType:
        return SourceType.CUSTOMER

    @override
    def get_model_class(self) -> type[Any]:
        return Customer

    @override
    def build_search_query(self, search_term: str) -> Any:
        return self.query_builder.build_search_query(search_term)
