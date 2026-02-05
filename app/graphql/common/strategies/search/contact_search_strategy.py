from typing import Any, override

from commons.db.v6.crm.contact_model import Contact
from sqlalchemy import func
from sqlalchemy.orm import InstrumentedAttribute

from app.graphql.common.builders.search_query_builder import SearchQueryBuilder
from app.graphql.common.interfaces.search_query_interface import SearchQueryStrategy
from app.graphql.common.strawberry.source_type import SourceType


class ContactSearchQueryBuilder(SearchQueryBuilder[Contact]):
    @override
    def get_searchable_fields(
        self,
    ) -> list[InstrumentedAttribute[str] | InstrumentedAttribute[str | None]]:
        return [
            Contact.first_name,
            Contact.last_name,
            Contact.email,
            Contact.phone,
            Contact.role,
        ]

    @override
    def get_computed_searchable_fields(self) -> list[Any]:
        return [func.concat(Contact.first_name, " ", Contact.last_name)]

    @override
    def get_title_field(self) -> Any:
        return func.concat(Contact.first_name, " ", Contact.last_name)

    @override
    def get_alias_field(self) -> Any | None:
        return func.coalesce(Contact.email, Contact.phone, Contact.role)

    @override
    def get_extra_info_field(self) -> Any | None:
        return Contact.phone


class ContactSearchStrategy(SearchQueryStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.query_builder = ContactSearchQueryBuilder(Contact, SourceType.CONTACT)

    @override
    def get_supported_source_type(self) -> SourceType:
        return SourceType.CONTACT

    @override
    def get_model_class(self) -> type[Any]:
        return Contact

    @override
    def build_search_query(self, search_term: str) -> Any:
        return self.query_builder.build_search_query(search_term)
