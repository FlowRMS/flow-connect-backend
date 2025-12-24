from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from commons.db.v6 import BaseModel
from sqlalchemy import Integer, func, literal, literal_column, or_, select
from sqlalchemy.orm import InstrumentedAttribute

from app.graphql.common.strawberry.search_types import SourceType

T = TypeVar("T", bound=BaseModel)


class SearchQueryBuilder(ABC, Generic[T]):
    def __init__(self, model: type[T], source_type: SourceType) -> None:
        super().__init__()
        self.model = model
        self.source_type = source_type

    @abstractmethod
    def get_searchable_fields(
        self,
    ) -> list[InstrumentedAttribute[str] | InstrumentedAttribute[str | None]]:
        pass

    @abstractmethod
    def get_title_field(self) -> InstrumentedAttribute[str] | Any:
        pass

    def get_alias_field(self) -> Any | None:
        return None

    def build_search_query(self, search_term: str) -> Any:
        search_pattern = f"%{search_term}%"
        searchable_fields = self.get_searchable_fields()

        similarity_calculations = [
            func.similarity(field, search_term) for field in searchable_fields
        ]

        where_conditions = [field.ilike(search_pattern) for field in searchable_fields]

        alias_field = self.get_alias_field()
        alias_column = (
            alias_field.label("alias")
            if alias_field is not None
            else literal(None).label("alias")
        )

        query = select(
            self.model.id,
            self.get_title_field().label("title"),
            alias_column,
            func.greatest(*similarity_calculations).label("similarity"),
        ).where(or_(*where_conditions))

        query = query.add_columns(
            literal_column(f"'{self.source_type.value}'", type_=Integer).label(
                "result_type"
            )
        )

        return query
