from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.container_types.services.container_type_service import (
    ContainerTypeService,
)
from app.graphql.v2.core.container_types.strawberry.container_type_response import (
    ContainerTypeResponse,
)


@strawberry.type
class ContainerTypesQueries:
    """GraphQL queries for ContainerType entity."""

    @strawberry.field
    @inject
    async def container_types(
        self,
        service: Injected[ContainerTypeService],
    ) -> list[ContainerTypeResponse]:
        """Get all container types ordered by display order."""
        container_types = await service.list_all()
        return ContainerTypeResponse.from_orm_model_list(container_types)

    @strawberry.field
    @inject
    async def container_type(
        self,
        id: UUID,
        service: Injected[ContainerTypeService],
    ) -> ContainerTypeResponse:
        """Get a container type by ID."""
        container_type = await service.get_by_id(id)
        return ContainerTypeResponse.from_orm_model(container_type)
