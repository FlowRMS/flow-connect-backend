from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.crm.companies.company_model import Company
from sqlalchemy.orm import joinedload, lazyload

from app.errors.common_errors import NotFoundError
from app.graphql.companies.repositories.companies_repository import CompaniesRepository
from app.graphql.companies.strawberry.company_input import CompanyInput


class CompaniesService:
    """Service for Companies entity business logic."""

    def __init__(
        self,
        repository: CompaniesRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def find_company_by_id(self, company_id: UUID) -> Company:
        company = await self.repository.get_by_id(
            company_id,
            options=[
                joinedload(Company.created_by),
                lazyload("*"),
            ],
        )

        if not company:
            raise NotFoundError(str(company_id))
        return company

    async def create_company(self, company_input: CompanyInput) -> Company:
        company = await self.repository.create(company_input.to_orm_model())
        return await self.find_company_by_id(company.id)

    async def delete_company(self, company_id: UUID | str) -> bool:
        if not await self.repository.exists(company_id):
            raise NotFoundError(str(company_id))
        return await self.repository.delete(company_id)

    async def get_company(self, company_id: UUID | str) -> Company:
        company = await self.repository.get_by_id(company_id)
        if not company:
            raise NotFoundError(str(company_id))
        return company

    async def find_companies_by_job_id(self, job_id: UUID) -> list[Company]:
        return await self.repository.find_by_job_id(job_id)

    async def update_company(
        self, company_id: UUID, company_input: CompanyInput
    ) -> Company:
        """
        Update an existing company.

        Args:
            company_id: The company ID to update
            company_input: The updated company data

        Returns:
            The updated company entity

        Raises:
            NotFoundError: If the company doesn't exist
        """
        if not await self.repository.exists(company_id):
            raise NotFoundError(str(company_id))

        company = company_input.to_orm_model()
        company.id = company_id
        _ = await self.repository.update(company)
        return await self.find_company_by_id(company_id)

    async def search_companies(
        self, search_term: str, limit: int = 20
    ) -> list[Company]:
        """
        Search companies by name.

        Args:
            search_term: The search term to match against company name
            limit: Maximum number of companies to return (default: 20)

        Returns:
            List of Company objects matching the search criteria
        """
        return await self.repository.search_by_name(search_term, limit)

    async def find_companies_by_task_id(self, task_id: UUID) -> list[Company]:
        """Find all companies linked to the given task ID."""
        return await self.repository.find_by_task_id(task_id)

    async def find_companies_by_note_id(self, note_id: UUID) -> list[Company]:
        """Find all companies linked to the given note ID."""
        return await self.repository.find_by_note_id(note_id)

    async def find_companies_by_contact_id(self, contact_id: UUID) -> list[Company]:
        """Find all companies linked to the given contact ID."""
        return await self.repository.find_by_contact_id(contact_id)
