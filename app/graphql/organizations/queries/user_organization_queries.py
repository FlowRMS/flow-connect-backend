import strawberry
from aioinject import Injected

from app.graphql.di import inject
from app.graphql.organizations.services.user_organization_service import (
    UserOrganizationService,
)
from app.graphql.organizations.strawberry.user_organization_types import (
    UserOrganizationResponse,
)


@strawberry.type
class UserOrganizationQueries:
    @strawberry.field()
    @inject
    async def user_organization(
        self,
        service: Injected[UserOrganizationService],
    ) -> UserOrganizationResponse:
        org = await service.get_user_organization()
        return UserOrganizationResponse.from_orm_model(org)
