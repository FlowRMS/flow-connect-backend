from typing import Any, override

from commons.db.v6.crm.jobs.jobs_model import Job
from sqlalchemy import func
from sqlalchemy.orm import InstrumentedAttribute

from app.graphql.common.builders.search_query_builder import SearchQueryBuilder
from app.graphql.common.interfaces.search_query_interface import SearchQueryStrategy
from app.graphql.common.strawberry.search_types import SourceType


class JobSearchQueryBuilder(SearchQueryBuilder[Job]):
    @override
    def get_searchable_fields(
        self,
    ) -> list[InstrumentedAttribute[str] | InstrumentedAttribute[str | None]]:
        return [
            Job.job_name,
            Job.job_type,
            Job.description,
            Job.structural_details,
        ]

    @override
    def get_title_field(self) -> InstrumentedAttribute[str]:
        return Job.job_name

    @override
    def get_alias_field(self) -> Any | None:
        return func.coalesce(Job.job_type, Job.description)


class JobSearchStrategy(SearchQueryStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.query_builder = JobSearchQueryBuilder(Job, SourceType.JOB)

    @override
    def get_supported_source_type(self) -> SourceType:
        return SourceType.JOB

    @override
    def get_model_class(self) -> type[Any]:
        return Job

    @override
    def build_search_query(self, search_term: str) -> Any:
        return self.query_builder.build_search_query(search_term)
