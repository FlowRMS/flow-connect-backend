"""GraphQL queries for Submittals entity."""

from typing import Optional
from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.submittals.services.submittals_service import SubmittalsService
from app.graphql.submittals.strawberry.enums import SubmittalStatusGQL
from app.graphql.submittals.strawberry.submittal_response import SubmittalResponse


@strawberry.type
class SubmittalsQueries:
    """GraphQL queries for Submittals entity."""

    @strawberry.field
    @inject
    async def submittal(
        self,
        service: Injected[SubmittalsService],
        id: UUID,
    ) -> Optional[SubmittalResponse]:
        """
        Get a submittal by ID.

        Args:
            id: UUID of the submittal

        Returns:
            SubmittalResponse or None if not found
        """
        submittal = await service.get_submittal(id)
        if not submittal:
            return None
        return SubmittalResponse.from_orm_model(submittal)

    @strawberry.field
    @inject
    async def submittals_by_quote(
        self,
        service: Injected[SubmittalsService],
        quote_id: UUID,
    ) -> list[SubmittalResponse]:
        """
        Get all submittals for a quote.

        Args:
            quote_id: UUID of the quote

        Returns:
            List of SubmittalResponse
        """
        submittals = await service.get_submittals_by_quote(quote_id)
        return SubmittalResponse.from_orm_model_list(submittals)

    @strawberry.field
    @inject
    async def submittals_by_job(
        self,
        service: Injected[SubmittalsService],
        job_id: UUID,
    ) -> list[SubmittalResponse]:
        """
        Get all submittals for a job.

        Args:
            job_id: UUID of the job

        Returns:
            List of SubmittalResponse
        """
        submittals = await service.get_submittals_by_job(job_id)
        return SubmittalResponse.from_orm_model_list(submittals)

    @strawberry.field
    @inject
    async def submittal_search(
        self,
        service: Injected[SubmittalsService],
        search_term: str = "",
        status: Optional[SubmittalStatusGQL] = None,
        limit: int = 50,
    ) -> list[SubmittalResponse]:
        """
        Search submittals.

        Args:
            search_term: Search term for submittal_number
            status: Optional status filter
            limit: Maximum number of results

        Returns:
            List of matching SubmittalResponse
        """
        from commons.db.v6.crm.submittals import SubmittalStatus

        status_filter = SubmittalStatus(status.value) if status else None
        submittals = await service.search_submittals(search_term, status_filter, limit)
        return SubmittalResponse.from_orm_model_list(submittals)
