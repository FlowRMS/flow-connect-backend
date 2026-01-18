"""Service for LinkRelation entity business logic."""

from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.link_relation_model import LinkRelation

from app.errors.common_errors import ConflictError, NotFoundError
from app.graphql.links.repositories.link_relations_repository import (
    LinkRelationsRepository,
)


class LinksService:
    """Service for LinkRelation entity business logic."""

    def __init__(
        self,
        repository: LinkRelationsRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def create_link(
        self,
        source_type: EntityType,
        source_id: UUID,
        target_type: EntityType,
        target_id: UUID,
    ) -> LinkRelation:
        # Check if link already exists (in either direction)
        if await self.repository.link_exists(
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
        ):
            msg = f"Link already exists between {source_type.name}:{source_id} and {target_type.name}:{target_id}"
            raise ConflictError(msg)

        link = LinkRelation(
            source_entity_type=source_type,
            source_entity_id=source_id,
            target_entity_type=target_type,
            target_entity_id=target_id,
        )
        return await self.repository.create(link)

    async def bulk_create_links(
        self,
        source_type: EntityType,
        source_id: UUID,
        target_type: EntityType,
        target_ids: list[UUID],
    ) -> list[LinkRelation]:
        if not target_ids:
            return []

        existing = await self.repository.get_existing_target_ids(
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_ids=target_ids,
        )

        new_target_ids = [tid for tid in target_ids if tid not in existing]
        if not new_target_ids:
            return []

        links = [
            LinkRelation(
                source_entity_type=source_type,
                source_entity_id=source_id,
                target_entity_type=target_type,
                target_entity_id=target_id,
            )
            for target_id in new_target_ids
        ]
        return await self.repository.bulk_create(links)

    async def get_link(self, link_id: UUID) -> LinkRelation:
        """Get a link by ID."""
        link = await self.repository.get_by_id(link_id)
        if not link:
            raise NotFoundError(str(link_id))
        return link

    async def get_links_for_entity(
        self,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> list[LinkRelation]:
        """Get all links for a specific entity (both as source and target)."""
        return await self.repository.get_links_for_entity(
            entity_type=entity_type,
            entity_id=entity_id,
        )

    async def get_links_from_source(
        self,
        source_type: EntityType,
        source_id: UUID,
    ) -> list[LinkRelation]:
        """Get all links from a specific source entity."""
        return await self.repository.get_links_from_source(
            source_type=source_type,
            source_id=source_id,
        )

    async def get_links_to_target(
        self,
        target_type: EntityType,
        target_id: UUID,
    ) -> list[LinkRelation]:
        """Get all links to a specific target entity."""
        return await self.repository.get_links_to_target(
            target_type=target_type,
            target_id=target_id,
        )

    async def delete_link(self, link_id: UUID) -> bool:
        """Delete a link by ID."""
        if not await self.repository.exists(link_id):
            raise NotFoundError(str(link_id))
        return await self.repository.delete(link_id)

    async def delete_link_by_entities(
        self,
        source_type: EntityType,
        source_id: UUID,
        target_type: EntityType,
        target_id: UUID,
    ) -> bool:
        """Delete a link between two specific entities."""
        result = await self.repository.delete_link(
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
        )
        if not result:
            msg = f"Link not found between {source_type.name}:{source_id} and {target_type.name}:{target_id}"
            raise NotFoundError(msg)
        return result
