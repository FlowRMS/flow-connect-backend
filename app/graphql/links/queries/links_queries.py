from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.crm.links.entity_type import EntityType

from app.graphql.inject import inject
from app.graphql.links.services.links_service import LinksService
from app.graphql.links.strawberry.link_response import LinkRelationType


@strawberry.type
class LinksQueries:
    """GraphQL queries for LinkRelation entity."""

    @strawberry.field
    @inject
    async def link(
        self,
        id: UUID,
        service: Injected[LinksService],
    ) -> LinkRelationType:
        """Get a link by ID."""
        return LinkRelationType.from_orm_model(await service.get_link(id))

    @strawberry.field
    @inject
    async def links_by_entity(
        self,
        entity_type: EntityType,
        entity_id: UUID,
        service: Injected[LinksService],
    ) -> list[LinkRelationType]:
        """Get all links for a specific entity (both as source and target)."""
        links = await service.get_links_for_entity(entity_type, entity_id)
        return [LinkRelationType.from_orm_model(link) for link in links]

    @strawberry.field
    @inject
    async def links_from_source(
        self,
        source_type: EntityType,
        source_id: UUID,
        service: Injected[LinksService],
    ) -> list[LinkRelationType]:
        """Get all links where the entity is the source."""
        links = await service.get_links_from_source(source_type, source_id)
        return [LinkRelationType.from_orm_model(link) for link in links]

    @strawberry.field
    @inject
    async def links_to_target(
        self,
        target_type: EntityType,
        target_id: UUID,
        service: Injected[LinksService],
    ) -> list[LinkRelationType]:
        """Get all links where the entity is the target."""
        links = await service.get_links_to_target(target_type, target_id)
        return [LinkRelationType.from_orm_model(link) for link in links]
