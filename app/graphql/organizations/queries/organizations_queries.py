import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.organizations.services.organization_service import OrganizationService
from app.graphql.organizations.strawberry.organization_types import OrganizationType


@strawberry.type
class OrganizationsQueries:
    @strawberry.field
    @inject
    async def organization(
        self,
        service: Injected[OrganizationService],
    ) -> OrganizationType | None:
        org = await service.get_organization()
        if not org:
            return None
        return OrganizationType.from_orm_model(org)
