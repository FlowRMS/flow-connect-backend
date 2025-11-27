"""Repository for LinkRelation entity."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.links.models.entity_type import EntityType
from app.graphql.links.models.link_relation_model import LinkRelation


class LinkRelationsRepository(BaseRepository[LinkRelation]):
    """Repository for LinkRelations entity."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, LinkRelation)

    async def get_links_for_entity(
        self,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> list[LinkRelation]:
        """Get all links for a specific entity (both as source and target)."""
        stmt = select(LinkRelation).where(
            (
                (LinkRelation.source_entity_type == entity_type)
                & (LinkRelation.source_entity_id == entity_id)
            )
            | (
                (LinkRelation.target_entity_type == entity_type)
                & (LinkRelation.target_entity_id == entity_id)
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_links_from_source(
        self,
        source_type: EntityType,
        source_id: UUID,
    ) -> list[LinkRelation]:
        """Get all links from a specific source entity."""
        stmt = select(LinkRelation).where(
            (LinkRelation.source_entity_type == source_type)
            & (LinkRelation.source_entity_id == source_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_links_to_target(
        self,
        target_type: EntityType,
        target_id: UUID,
    ) -> list[LinkRelation]:
        """Get all links to a specific target entity."""
        stmt = select(LinkRelation).where(
            (LinkRelation.target_entity_type == target_type)
            & (LinkRelation.target_entity_id == target_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def link_exists(
        self,
        source_type: EntityType,
        source_id: UUID,
        target_type: EntityType,
        target_id: UUID,
    ) -> bool:
        """Check if a link already exists between two entities (in either direction)."""
        stmt = select(LinkRelation).where(
            (
                (LinkRelation.source_entity_type == source_type)
                & (LinkRelation.source_entity_id == source_id)
                & (LinkRelation.target_entity_type == target_type)
                & (LinkRelation.target_entity_id == target_id)
            )
            | (
                (LinkRelation.source_entity_type == target_type)
                & (LinkRelation.source_entity_id == target_id)
                & (LinkRelation.target_entity_type == source_type)
                & (LinkRelation.target_entity_id == source_id)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def delete_link(
        self,
        source_type: EntityType,
        source_id: UUID,
        target_type: EntityType,
        target_id: UUID,
    ) -> bool:
        """Delete a specific link between two entities (in either direction)."""
        # First find the link
        stmt = select(LinkRelation).where(
            (
                (LinkRelation.source_entity_type == source_type)
                & (LinkRelation.source_entity_id == source_id)
                & (LinkRelation.target_entity_type == target_type)
                & (LinkRelation.target_entity_id == target_id)
            )
            | (
                (LinkRelation.source_entity_type == target_type)
                & (LinkRelation.source_entity_id == target_id)
                & (LinkRelation.target_entity_type == source_type)
                & (LinkRelation.target_entity_id == source_id)
            )
        )
        result = await self.session.execute(stmt)
        link = result.scalar_one_or_none()

        if link is None:
            return False

        return await self.delete(link.id)
