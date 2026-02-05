from typing import Any, override

from commons.db.v6.crm.notes.note_model import Note
from sqlalchemy.orm import InstrumentedAttribute

from app.graphql.common.builders.search_query_builder import SearchQueryBuilder
from app.graphql.common.interfaces.search_query_interface import SearchQueryStrategy
from app.graphql.common.strawberry.source_type import SourceType


class NoteSearchQueryBuilder(SearchQueryBuilder[Note]):
    @override
    def get_searchable_fields(
        self,
    ) -> list[InstrumentedAttribute[str] | InstrumentedAttribute[str | None]]:
        return [Note.title, Note.content]

    @override
    def get_title_field(self) -> InstrumentedAttribute[str]:
        return Note.title

    @override
    def get_alias_field(self) -> Any | None:
        return Note.content


class NoteSearchStrategy(SearchQueryStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.query_builder = NoteSearchQueryBuilder(Note, SourceType.NOTE)

    @override
    def get_supported_source_type(self) -> SourceType:
        return SourceType.NOTE

    @override
    def get_model_class(self) -> type[Any]:
        return Note

    @override
    def build_search_query(self, search_term: str) -> Any:
        return self.query_builder.build_search_query(search_term)
