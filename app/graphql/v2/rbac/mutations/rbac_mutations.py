import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.rbac.services.rbac_service import RbacService
from app.graphql.v2.rbac.strawberry.rbac_grid_input import RbacGridInput
from app.graphql.v2.rbac.strawberry.rbac_grid_response import RbacGridResponse


@strawberry.type
class RbacMutations:
    @strawberry.mutation
    @inject
    async def update_rbac_grid(
        self,
        rbac_grid: list[RbacGridInput],
        service: Injected[RbacService],
    ) -> list[RbacGridResponse]:
        return await service.update_rbac_grid(rbac_grid)