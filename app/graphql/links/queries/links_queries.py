"""GraphQL queries for LinkRelation entity."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.links.models.entity_type import EntityType
from app.graphql.links.services.links_service import LinksService
from app.graphql.links.strawberry.link_response import LinkRelationType


@strawberry.type
class LinksQueries:
    @strawberry.field
    @inject
    async def links_for_entity(
        self,
        entity_type: EntityType,
        entity_id: UUID,
        service: Injected[LinksService],
    ) -> list[LinkRelationType]:
        """Get all links for a specific entity (both as source and target)."""
        links = await service.get_links_for_entity(
            entity_type=entity_type,
            entity_id=entity_id,
        )
        return LinkRelationType.from_orm_model_list(links)

    @strawberry.field
    @inject
    async def links_from_source(
        self,
        source_type: EntityType,
        source_id: UUID,
        service: Injected[LinksService],
    ) -> list[LinkRelationType]:
        """Get all links from a specific source entity."""
        links = await service.get_links_from_source(
            source_type=source_type,
            source_id=source_id,
        )
        return LinkRelationType.from_orm_model_list(links)

    @strawberry.field
    @inject
    async def links_to_target(
        self,
        target_type: EntityType,
        target_id: UUID,
        service: Injected[LinksService],
    ) -> list[LinkRelationType]:
        """Get all links to a specific target entity."""
        links = await service.get_links_to_target(
            target_type=target_type,
            target_id=target_id,
        )
        return LinkRelationType.from_orm_model_list(links)
