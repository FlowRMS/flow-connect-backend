"""Service layer for Jobs entity with business logic."""

from uuid import UUID

from commons.auth import AuthInfo

from app.errors.common_errors import NotFoundError
from app.graphql.checks.services.check_service import CheckService
from app.graphql.checks.strawberry.check_response import CheckResponse
from app.graphql.companies.services.companies_service import CompaniesService
from app.graphql.companies.strawberry.company_response import CompanyResponse
from app.graphql.contacts.services.contacts_service import ContactsService
from app.graphql.contacts.strawberry.contact_response import ContactResponse
from app.graphql.customers.services.customer_service import CustomerService
from app.graphql.customers.strawberry.customer_response import CustomerResponse
from app.graphql.factories.services.factory_service import FactoryService
from app.graphql.factories.strawberry.factory_response import FactoryResponse
from app.graphql.invoices.services.invoice_service import InvoiceService
from app.graphql.invoices.strawberry.invoice_response import InvoiceResponse
from app.graphql.jobs.models.jobs_model import Job
from app.graphql.jobs.repositories.jobs_repository import JobsRepository
from app.graphql.jobs.strawberry.job_input import JobInput
from app.graphql.jobs.strawberry.job_related_entities_response import (
    JobRelatedEntitiesResponse,
)
from app.graphql.links.models.entity_type import EntityType
from app.graphql.orders.services.order_service import OrderService
from app.graphql.orders.strawberry.order_response import OrderResponse
from app.graphql.pre_opportunities.services.pre_opportunities_service import (
    PreOpportunitiesService,
)
from app.graphql.pre_opportunities.strawberry.pre_opportunity_lite_response import (
    PreOpportunityLiteResponse,
)
from app.graphql.products.services.product_service import ProductService
from app.graphql.products.strawberry.product_response import ProductResponse
from app.graphql.quotes.services.quote_service import QuoteService
from app.graphql.quotes.strawberry.quote_response import QuoteResponse


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
        quote_service: QuoteService,
        order_service: OrderService,
        invoice_service: InvoiceService,
        check_service: CheckService,
        factory_service: FactoryService,
        product_service: ProductService,
        customer_service: CustomerService,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info
        self.companies_service = companies_service
        self.contacts_service = contacts_service
        self.pre_opportunities_service = pre_opportunities_service
        self.quote_service = quote_service
        self.order_service = order_service
        self.invoice_service = invoice_service
        self.check_service = check_service
        self.factory_service = factory_service
        self.product_service = product_service
        self.customer_service = customer_service

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
            JobRelatedEntitiesResponse containing all related entities

        Raises:
            NotFoundError: If the job doesn't exist
        """
        # Verify job exists
        if not await self.repository.exists(job_id):
            raise NotFoundError(str(job_id))

        # Fetch related entities
        pre_opportunities = await self.pre_opportunities_service.get_by_job_id(job_id)
        contacts = await self.contacts_service.find_contacts_by_job_id(job_id)
        companies = await self.companies_service.find_companies_by_job_id(job_id)
        quotes = await self.quote_service.find_quotes_by_job_id(job_id)
        orders = await self.order_service.find_orders_by_job_id(job_id)
        invoices = await self.invoice_service.find_invoices_by_job_id(job_id)
        checks = await self.check_service.find_checks_by_job_id(job_id)
        factories = await self.factory_service.find_by_entity(EntityType.JOB, job_id)
        products = await self.product_service.find_by_entity(EntityType.JOB, job_id)
        customers = await self.customer_service.find_by_entity(EntityType.JOB, job_id)

        return JobRelatedEntitiesResponse(
            pre_opportunities=PreOpportunityLiteResponse.from_orm_model_list(
                pre_opportunities
            ),
            contacts=ContactResponse.from_orm_model_list(contacts),
            companies=CompanyResponse.from_orm_model_list(companies),
            quotes=QuoteResponse.from_orm_model_list(quotes),
            orders=OrderResponse.from_orm_model_list(orders),
            invoices=InvoiceResponse.from_orm_model_list(invoices),
            checks=CheckResponse.from_orm_model_list(checks),
            factories=FactoryResponse.from_orm_model_list(factories),
            products=ProductResponse.from_orm_model_list(products),
            customers=CustomerResponse.from_orm_model_list(customers),
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

    async def get_jobs_by_task(self, task_id: UUID) -> list[Job]:
        """Find all jobs linked to the given task ID."""
        return await self.repository.find_by_task_id(task_id)

    async def get_jobs_by_note(self, note_id: UUID) -> list[Job]:
        """Find all jobs linked to the given note ID."""
        return await self.repository.find_by_note_id(note_id)
