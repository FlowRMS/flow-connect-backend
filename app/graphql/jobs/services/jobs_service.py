"""Service layer for Jobs entity with business logic."""

from uuid import UUID

from commons.auth import AuthInfo

from app.errors.common_errors import NotFoundError
from app.graphql.companies.services.companies_service import CompaniesService
from app.graphql.companies.strawberry.company_response import CompanyResponse
from app.graphql.contacts.services.contacts_service import ContactsService
from app.graphql.contacts.strawberry.contact_response import ContactResponse
from app.graphql.jobs.models.jobs_model import Job
from app.graphql.jobs.repositories.jobs_repository import JobsRepository
from app.graphql.jobs.strawberry.job_input import JobInput
from app.graphql.jobs.strawberry.job_related_entities_response import (
    JobRelatedEntitiesResponse,
)
from app.graphql.pre_opportunities.services.pre_opportunities_service import (
    PreOpportunitiesService,
)
from app.graphql.pre_opportunities.strawberry.pre_opportunity_lite_response import (
    PreOpportunityLiteResponse,
)


class JobsService:
    """
    Service for Jobs entity business logic.

    Handles validation, authorization, and orchestration of job operations.
    """

    def __init__(
        self,
        repository: JobsRepository,
        auth_info: AuthInfo,
        companies_service: CompaniesService,
        contacts_service: ContactsService,
        pre_opportunities_service: PreOpportunitiesService,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info
        self.companies_service = companies_service
        self.contacts_service = contacts_service
        self.pre_opportunities_service = pre_opportunities_service

    async def create_job(
        self,
        job_input: JobInput,
    ) -> Job:
        job = job_input.to_orm_model()
        return await self.repository.create(job)

    async def delete_job(self, job_id: UUID | str) -> bool:
        """
        Delete a job.

        Args:
            job_id: The job ID

        Returns:
            True if deleted successfully

        Raises:
            JobNotFoundError: If the job doesn't exist
        """
        if not await self.repository.exists(job_id):
            raise NotFoundError(str(job_id))

        return await self.repository.delete(job_id)

    async def get_job(self, job_id: UUID | str) -> Job:
        """
        Get a job by ID.

        Args:
            job_id: The job ID

        Returns:
            The job entity

        Raises:
            JobNotFoundError: If the job doesn't exist
        """
        job = await self.repository.get_by_id(job_id)
        if not job:
            raise NotFoundError(str(job_id))
        return job

    async def get_job_related_entities(
        self, job_id: UUID
    ) -> JobRelatedEntitiesResponse:
        """
        Get all entities related to a job.

        Args:
            job_id: The job ID

        Returns:
            JobRelatedEntitiesResponse containing pre_opportunities, contacts, and companies

        Raises:
            NotFoundError: If the job doesn't exist
        """
        # Verify job exists
        if not await self.repository.exists(job_id):
            raise NotFoundError(str(job_id))

        # Fetch related entities in parallel
        pre_opportunities = await self.pre_opportunities_service.get_by_job_id(job_id)
        contacts = await self.contacts_service.find_contacts_by_job_id(job_id)
        companies = await self.companies_service.find_companies_by_job_id(job_id)

        return JobRelatedEntitiesResponse(
            pre_opportunities=PreOpportunityLiteResponse.from_orm_model_list(
                pre_opportunities
            ),
            contacts=ContactResponse.from_orm_model_list(contacts),
            companies=CompanyResponse.from_orm_model_list(companies),
        )

    async def search_jobs(self, search_term: str, limit: int = 20) -> list[Job]:
        """
        Search jobs by name.

        Args:
            search_term: The search term to match against job name
            limit: Maximum number of jobs to return (default: 20)

        Returns:
            List of Job objects matching the search criteria
        """
        return await self.repository.search_by_name(search_term, limit)

    async def get_jobs_by_contact(self, contact_id: UUID) -> list[Job]:
        """
        Get all jobs linked to a specific contact.

        Args:
            contact_id: The contact ID to find jobs for

        Returns:
            List of Job objects linked to the given contact ID
        """
        return await self.repository.find_by_contact_id(contact_id)

    async def get_jobs_by_company(self, company_id: UUID) -> list[Job]:
        """
        Get all jobs linked to a specific company.

        Args:
            company_id: The company ID to find jobs for

        Returns:
            List of Job objects linked to the given company ID
        """
        return await self.repository.find_by_company_id(company_id)

    async def update_job(self, job_id: UUID, job_input: JobInput) -> Job:
        """
        Update an existing job.

        Args:
            job_id: The job ID to update
            job_input: The updated job data

        Returns:
            The updated job entity

        Raises:
            NotFoundError: If the job doesn't exist
        """
        if not await self.repository.exists(job_id):
            raise NotFoundError(str(job_id))

        job = job_input.to_orm_model()
        job.id = job_id
        return await self.repository.update(job)
