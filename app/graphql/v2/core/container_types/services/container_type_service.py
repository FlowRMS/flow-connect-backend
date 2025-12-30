"""Service layer for container type operations."""

from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6 import ContainerType

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.container_types.repositories import ContainerTypesRepository
from app.graphql.v2.core.container_types.strawberry.container_type_input import (
    ContainerTypeInput,
)


class ContainerTypeService:
    """Service for container type operations."""

    def __init__(
        self,
        repository: ContainerTypesRepository,
        auth_info: AuthInfo,
    ) -> None:
        self.repository = repository
        self.auth_info = auth_info

    async def get_by_id(self, container_type_id: UUID) -> ContainerType:
        """Get a container type by ID."""
        container_type = await self.repository.get_by_id(container_type_id)
        if not container_type:
            raise NotFoundError(f"Container type with id {container_type_id} not found")
        return container_type

    async def list_all(self) -> list[ContainerType]:
        """Get all container types ordered by display order."""
        return await self.repository.list_all_ordered()

    async def create(self, input: ContainerTypeInput) -> ContainerType:
        """Create a new container type."""
        container_type = input.to_orm_model()

        # Auto-assign position if not provided
        if container_type.position == 0:
            max_position = await self.repository.get_max_position()
            container_type.position = max_position + 1

        return await self.repository.create(container_type)

    async def update(
        self, container_type_id: UUID, input: ContainerTypeInput
    ) -> ContainerType:
        """Update a container type."""
        existing = await self.repository.get_by_id(container_type_id)
        if not existing:
            raise NotFoundError(f"Container type with id {container_type_id} not found")

        container_type = input.to_orm_model()
        container_type.id = container_type_id

        # Keep existing position if not provided
        if container_type.position == 0:
            container_type.position = existing.position

        return await self.repository.update(container_type)

    async def delete(self, container_type_id: UUID) -> bool:
        """Delete a container type."""
        if not await self.repository.exists(container_type_id):
            raise NotFoundError(f"Container type with id {container_type_id} not found")
        return await self.repository.delete(container_type_id)

    async def reorder(self, ordered_ids: list[UUID]) -> list[ContainerType]:
        """Reorder container types based on the provided ID list."""
        return await self.repository.reorder(ordered_ids)
