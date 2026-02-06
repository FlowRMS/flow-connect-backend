from commons.auth import AuthInfo

from app.graphql.connections.repositories.user_org_repository import UserOrgRepository
from app.graphql.organizations.models import RemoteOrg
from app.graphql.organizations.repositories.organization_search_repository import (
    OrganizationSearchRepository,
)


class UserOrganizationService:
    def __init__(
        self,
        user_org_repository: UserOrgRepository,
        org_search_repository: OrganizationSearchRepository,
        auth_info: AuthInfo,
    ) -> None:
        self.user_org_repository = user_org_repository
        self.org_search_repository = org_search_repository
        self.auth_info = auth_info

    async def get_user_organization(self) -> RemoteOrg:
        if self.auth_info.auth_provider_id is None:
            raise ValueError("Auth provider ID is required")
        org_id = await self.user_org_repository.get_user_org_id(
            self.auth_info.auth_provider_id
        )
        org = await self.org_search_repository.get_by_id(org_id)
        if org is None:
            raise ValueError(f"User organization not found: {org_id}")
        return org
