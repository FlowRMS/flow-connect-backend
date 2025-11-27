"""Paginated landing page response types for GraphQL queries."""

from typing import Any, Self

import strawberry
from commons.graphql.filter_types import Filter
from commons.graphql.order_by_types import OrderBy
from commons.graphql.pagination import get_pagination_window as _get_pagination_window
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.companies.strawberry.company_landing_page_response import (
    CompanyLandingPageResponse,
)
from app.graphql.contacts.strawberry.contact_landing_page_response import (
    ContactLandingPageResponse,
)
from app.graphql.jobs.strawberry.job_landing_page_response import JobLandingPageResponse

LandingRecord = strawberry.union(
    name="LandingRecord",
    types=[
        JobLandingPageResponse,
        CompanyLandingPageResponse,
        ContactLandingPageResponse,
    ],
)


@strawberry.type(name="GenericLandingPage")
class PaginatedLandingPageInterface:
    """Generic paginated landing page response with records and total count."""

    records: list[LandingRecord]
    total: int

    @classmethod
    async def get_pagination_window(
        cls,
        session: AsyncSession,
        stmt: Select[Any],
        record_type: type[Any],
        record_type_gql: type[Any],
        filters: list[Filter] | None = None,
        order_by: OrderBy | list[OrderBy] | None = None,
        limit: int | None = 10,
        offset: int | None = 0,
    ) -> Self:
        """
        Generate a paginated landing page response.

        Args:
            session: SQLAlchemy async session
            stmt: Base SQLAlchemy select statement
            record_type: The ORM model type (e.g., Job, Task)
            record_type_gql: The GraphQL/DTO type with from_orm_model_list method
            filters: Optional list of Filter objects to apply to the query
            order_by: Optional OrderBy or list of OrderBy objects for sorting
            limit: Maximum number of records to return (default: 10)
            offset: Number of records to skip (default: 0)

        Returns:
            PaginatedLandingPageInterface with records and total count
        """
        records, total = await _get_pagination_window(
            session=session,
            query=stmt,
            record_type=record_type,
            record_type_gql=record_type_gql,
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset,
        )

        return cls(records=records, total=total)
