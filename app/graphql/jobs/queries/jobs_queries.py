"""GraphQL queries for Jobs entity."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.jobs.services.jobs_service import JobsService
from app.graphql.jobs.services.status_service import JobStatusService
from app.graphql.jobs.strawberry.job_related_entities_response import (
    JobRelatedEntitiesResponse,
)
from app.graphql.jobs.strawberry.job_response import JobType
from app.graphql.jobs.strawberry.status_response import JobStatusType


@strawberry.type
class JobsQueries:
    """GraphQL queries for Jobs entity."""

    @strawberry.field
    def dummy_field(self) -> str:
        """A dummy field to ensure the class is not empty."""
        return "JobsQueries is active"

    @strawberry.field
    @inject
    async def job(
        self,
        id: UUID,
        service: Injected[JobsService],
    ) -> JobType:
        return JobType.from_orm_model(await service.get_job(id))

    @strawberry.field
    @inject
    async def job_statuses(
        self,
        service: Injected[JobStatusService],
    ) -> list[JobStatusType]:
        return JobStatusType.from_orm_model_list(await service.get_all_statuses())

    @strawberry.field
    @inject
    async def job_related_entities(
        self,
        job_id: UUID,
        service: Injected[JobsService],
    ) -> JobRelatedEntitiesResponse:
        """
        Get all entities related to a job.

        Args:
            job_id: The job ID to get related entities for
            service: Injected JobsService

        Returns:
            JobRelatedEntitiesResponse containing pre_opportunities, contacts, and companies
        """
        return await service.get_job_related_entities(job_id)

    @strawberry.field
    @inject
    async def job_search(
        self,
        service: Injected[JobsService],
        search_term: str,
        limit: int = 20,
    ) -> list[JobType]:
        """
        Search jobs by name.

        Args:
            search_term: The search term to match against job name
            limit: Maximum number of jobs to return (default: 20)

        Returns:
            List of JobType objects matching the search criteria
        """
        return JobType.from_orm_model_list(
            await service.search_jobs(search_term, limit)
        )

    @strawberry.field
    @inject
    async def jobs_by_contact(
        self,
        contact_id: UUID,
        service: Injected[JobsService],
    ) -> list[JobType]:
        """
        Get all jobs linked to a specific contact.

        Args:
            contact_id: The contact ID to find jobs for
            service: Injected JobsService

        Returns:
            List of JobType objects linked to the given contact ID
        """
        return JobType.from_orm_model_list(
            await service.get_jobs_by_contact(contact_id)
        )

    @strawberry.field
    @inject
    async def jobs_by_company(
        self,
        company_id: UUID,
        service: Injected[JobsService],
    ) -> list[JobType]:
        """
        Get all jobs linked to a specific company.

        Args:
            company_id: The company ID to find jobs for
            service: Injected JobsService

        Returns:
            List of JobType objects linked to the given company ID
        """
        return JobType.from_orm_model_list(
            await service.get_jobs_by_company(company_id)
        )
