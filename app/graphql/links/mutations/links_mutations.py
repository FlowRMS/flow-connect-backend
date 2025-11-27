"""GraphQL mutations for LinkRelation entity."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.links.services.links_service import LinksService
from app.graphql.links.strawberry.link_input import (
    DeleteLinkByEntitiesInput,
    LinkRelationInput,
)
from app.graphql.links.strawberry.link_response import LinkRelationType


@strawberry.type
class LinksMutations:
    """GraphQL mutations for LinkRelation entity."""

    @strawberry.mutation
    @inject
    async def create_link(
        self,
        input: LinkRelationInput,
        service: Injected[LinksService],
    ) -> LinkRelationType:
        """Create a new link between two entities."""
        link = await service.create_link(
            source_type=input.source_entity_type,
            source_id=input.source_entity_id,
            target_type=input.target_entity_type,
            target_id=input.target_entity_id,
        )
        return LinkRelationType.from_orm_model(link)

    @strawberry.mutation
    @inject
    async def delete_link(
        self,
        id: UUID,
        service: Injected[LinksService],
    ) -> bool:
        """Delete a link by ID."""
        return await service.delete_link(link_id=id)

    @strawberry.mutation
    @inject
    async def delete_link_by_entities(
        self,
        input: DeleteLinkByEntitiesInput,
        service: Injected[LinksService],
    ) -> bool:
        """Delete a link between two specific entities."""
        return await service.delete_link_by_entities(
            source_type=input.source_entity_type,
            source_id=input.source_entity_id,
            target_type=input.target_entity_type,
            target_id=input.target_entity_id,
        )
