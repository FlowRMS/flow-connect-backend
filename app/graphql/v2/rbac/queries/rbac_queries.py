import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.rbac.services.rbac_service import RbacService
from app.graphql.v2.rbac.strawberry.rbac_grid_response import RbacGridResponse


@strawberry.type
class RbacQueries:
    @strawberry.field
    @inject
    async def get_rbac_grid(
        self,
        service: Injected[RbacService],
    ) -> list[RbacGridResponse]:
        return await service.get_rbac_grid()
