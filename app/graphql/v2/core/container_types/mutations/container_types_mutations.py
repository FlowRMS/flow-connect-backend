from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.container_types.services.container_type_service import (
    ContainerTypeService,
)
from app.graphql.v2.core.container_types.strawberry.container_type_input import (
    ContainerTypeInput,
)
from app.graphql.v2.core.container_types.strawberry.container_type_response import (
    ContainerTypeResponse,
)


@strawberry.type
class ContainerTypesMutations:
    """GraphQL mutations for ContainerType entity."""

    @strawberry.mutation
    @inject
    async def create_container_type(
        self,
        input: ContainerTypeInput,
        service: Injected[ContainerTypeService],
    ) -> ContainerTypeResponse:
        container_type = await service.create(input)
        return ContainerTypeResponse.from_orm_model(container_type)

    @strawberry.mutation
    @inject
    async def update_container_type(
        self,
        id: UUID,
        input: ContainerTypeInput,
        service: Injected[ContainerTypeService],
    ) -> ContainerTypeResponse:
        container_type = await service.update(id, input)
        return ContainerTypeResponse.from_orm_model(container_type)

    @strawberry.mutation
    @inject
    async def delete_container_type(
        self,
        id: UUID,
        service: Injected[ContainerTypeService],
    ) -> bool:
        return await service.delete(id)

    @strawberry.mutation
    @inject
    async def reorder_container_types(
        self,
        ordered_ids: list[UUID],
        service: Injected[ContainerTypeService],
    ) -> list[ContainerTypeResponse]:
        """Reorder container types based on the provided ID list.

        The order of IDs in the list determines the new display order.
        """
        container_types = await service.reorder(ordered_ids)
        return ContainerTypeResponse.from_orm_model_list(container_types)
