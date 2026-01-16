from uuid import UUID

from commons.db.v6.crm.companies import CompanyTypeEntity

from app.errors.common_errors import NotFoundError
from app.graphql.companies.repositories.company_types_repository import (
    CompanyTypesRepository,
)
from app.graphql.companies.strawberry.company_type_input import (
    CreateCompanyTypeInput,
    UpdateCompanyTypeInput,
)


class CompanyTypesService:
    def __init__(self, repository: CompanyTypesRepository) -> None:
        self.repository = repository

    async def list_types(self, include_inactive: bool = False) -> list[CompanyTypeEntity]:
        if include_inactive:
            return await self.repository.list_all_ordered()
        return await self.repository.list_active()

    async def get_type_by_id(self, type_id: UUID) -> CompanyTypeEntity:
        company_type = await self.repository.get_by_id(type_id)
        if not company_type:
            raise NotFoundError(str(type_id))
        return company_type

    async def create_type(self, input: CreateCompanyTypeInput) -> CompanyTypeEntity:
        company_type = input.to_orm_model()
        return await self.repository.create(company_type)

    async def update_type(
        self, type_id: UUID, input: UpdateCompanyTypeInput
    ) -> CompanyTypeEntity:
        existing = await self.repository.get_by_id(type_id)
        if not existing:
            raise NotFoundError(str(type_id))

        company_type = input.to_orm_model()
        company_type.id = type_id
        return await self.repository.update(company_type)

    async def delete_type(self, type_id: UUID) -> bool:
        existing = await self.repository.get_by_id(type_id)
        if not existing:
            raise NotFoundError(str(type_id))

        existing.is_active = False
        await self.repository.update(existing)
        return True
