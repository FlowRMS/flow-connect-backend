from commons.auth import AuthInfo
from commons.db.v6 import Organization

from app.errors.common_errors import NotFoundError
from app.graphql.organizations.repositories.organization_repository import (
    OrganizationRepository,
)
from app.graphql.organizations.strawberry.organization_inputs import OrganizationInput


class OrganizationService:
    def __init__(
        self,
        repository: OrganizationRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_organization(self) -> Organization | None:
        return await self.repository.get_single()

    async def create_organization(
        self,
        organization_input: OrganizationInput,
    ) -> Organization:
        if await self.repository.organization_exists():
            raise ValueError("Organization already exists for this tenant")

        organization = organization_input.to_orm_model()
        return await self.repository.create(organization)

    async def update_organization(
        self,
        organization_input: OrganizationInput,
    ) -> Organization:
        existing = await self.repository.get_single()
        if not existing:
            raise NotFoundError("Organization not found")

        organization = organization_input.to_orm_model()
        organization.id = existing.id
        return await self.repository.update(organization)
