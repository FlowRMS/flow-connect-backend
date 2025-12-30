from typing import Any, override

from commons.db.v6.crm.spec_sheets.spec_sheet_model import SpecSheet
from sqlalchemy import func
from sqlalchemy.orm import InstrumentedAttribute

from app.graphql.common.builders.search_query_builder import SearchQueryBuilder
from app.graphql.common.interfaces.search_query_interface import SearchQueryStrategy
from app.graphql.common.strawberry.search_types import SourceType


class SpecSheetSearchQueryBuilder(SearchQueryBuilder[SpecSheet]):
    @override
    def get_searchable_fields(
        self,
    ) -> list[InstrumentedAttribute[str] | InstrumentedAttribute[str | None]]:
        return [SpecSheet.display_name, SpecSheet.file_name, SpecSheet.folder_path]

    @override
    def get_title_field(self) -> InstrumentedAttribute[str]:
        return SpecSheet.display_name

    @override
    def get_alias_field(self) -> Any | None:
        return func.coalesce(SpecSheet.file_name, SpecSheet.folder_path)


class SpecSheetSearchStrategy(SearchQueryStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.query_builder = SpecSheetSearchQueryBuilder(
            SpecSheet, SourceType.SPEC_SHEET
        )

    @override
    def get_supported_source_type(self) -> SourceType:
        return SourceType.SPEC_SHEET

    @override
    def get_model_class(self) -> type[Any]:
        return SpecSheet

    @override
    def build_search_query(self, search_term: str) -> Any:
        return self.query_builder.build_search_query(search_term)
