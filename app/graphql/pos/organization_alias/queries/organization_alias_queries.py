import strawberry
from aioinject import Injected

from app.graphql.di import inject
from app.graphql.pos.organization_alias.services.organization_alias_service import (
    OrganizationAliasService,
)
from app.graphql.pos.organization_alias.strawberry.organization_alias_types import (
    OrganizationAliasGroupResponse,
)


@strawberry.type
class OrganizationAliasQueries:
    @strawberry.field()
    @inject
    async def organization_aliases(
        self,
        service: Injected[OrganizationAliasService],
    ) -> list[OrganizationAliasGroupResponse]:
        groups = await service.get_all_aliases_grouped()
        return [OrganizationAliasGroupResponse.from_alias_group(g) for g in groups]
