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

    def get_extra_info_field(self) -> Any | None:
        return None

    def get_computed_searchable_fields(self) -> list[Any]:
        return []

    def get_joins(self) -> list[tuple[Any, Any]]:
        return []

    def build_search_query(self, search_term: str) -> Any:
        search_pattern = f"%{search_term}%"
        searchable_fields = self.get_searchable_fields()
        computed_fields = self.get_computed_searchable_fields()
        all_fields = [*searchable_fields, *computed_fields]

        similarity_calculations = [
            func.similarity(field, search_term) for field in all_fields
        ]

        where_conditions = [field.ilike(search_pattern) for field in all_fields]

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
        )

        for target, onclause in self.get_joins():
            query = query.outerjoin(target, onclause)

        query = query.where(or_(*where_conditions))

        query = query.add_columns(
            literal_column(f"'{self.source_type.value}'", type_=Integer).label(
                "result_type"
            )
        )

        extra_info_field = self.get_extra_info_field()
        extra_info_column = (
            extra_info_field.label("extra_info")
            if extra_info_field is not None
            else literal(None).label("extra_info")
        )
        query = query.add_columns(extra_info_column)

        return query
