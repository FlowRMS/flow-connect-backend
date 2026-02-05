from typing import Any, override

from commons.db.v6.crm.tasks.task_model import Task
from sqlalchemy.orm import InstrumentedAttribute

from app.graphql.common.builders.search_query_builder import SearchQueryBuilder
from app.graphql.common.interfaces.search_query_interface import SearchQueryStrategy
from app.graphql.common.strawberry.source_type import SourceType


class TaskSearchQueryBuilder(SearchQueryBuilder[Task]):
    @override
    def get_searchable_fields(
        self,
    ) -> list[InstrumentedAttribute[str] | InstrumentedAttribute[str | None]]:
        return [Task.title, Task.description]

    @override
    def get_title_field(self) -> InstrumentedAttribute[str]:
        return Task.title

    @override
    def get_alias_field(self) -> Any | None:
        return Task.description


class TaskSearchStrategy(SearchQueryStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.query_builder = TaskSearchQueryBuilder(Task, SourceType.TASK)

    @override
    def get_supported_source_type(self) -> SourceType:
        return SourceType.TASK

    @override
    def get_model_class(self) -> type[Any]:
        return Task

    @override
    def build_search_query(self, search_term: str) -> Any:
        return self.query_builder.build_search_query(search_term)
