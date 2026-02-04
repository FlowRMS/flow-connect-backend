from typing import Any, override

from commons.db.v6.crm.companies.company_model import Company
from sqlalchemy import func
from sqlalchemy.orm import InstrumentedAttribute

from app.graphql.common.builders.search_query_builder import SearchQueryBuilder
from app.graphql.common.interfaces.search_query_interface import SearchQueryStrategy
from app.graphql.common.strawberry.source_type import SourceType


class CompanySearchQueryBuilder(SearchQueryBuilder[Company]):
    @override
    def get_searchable_fields(
        self,
    ) -> list[InstrumentedAttribute[str] | InstrumentedAttribute[str | None]]:
        return [Company.name, Company.website, Company.phone]

    @override
    def get_title_field(self) -> InstrumentedAttribute[str]:
        return Company.name

    @override
    def get_alias_field(self) -> Any | None:
        return func.coalesce(Company.website, Company.phone)


class CompanySearchStrategy(SearchQueryStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.query_builder = CompanySearchQueryBuilder(Company, SourceType.COMPANY)

    @override
    def get_supported_source_type(self) -> SourceType:
        return SourceType.COMPANY

    @override
    def get_model_class(self) -> type[Any]:
        return Company

    @override
    def build_search_query(self, search_term: str) -> Any:
        return self.query_builder.build_search_query(search_term)
