from uuid import UUID

from commons.auth import AuthInfo

from app.errors.common_errors import NotFoundError
from app.graphql.companies.models.company_model import Company
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

    async def create_company(self, company_input: CompanyInput) -> Company:
        company = company_input.to_orm_model()
        return await self.repository.create(company)

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
        return await self.repository.update(company)
