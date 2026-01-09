"""Repository for LinkRelation entity."""

from uuid import UUID

from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.link_relation_model import LinkRelation
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


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

    async def get_existing_target_ids(
        self,
        source_type: EntityType,
        source_id: UUID,
        target_type: EntityType,
        target_ids: list[UUID],
    ) -> set[UUID]:
        if not target_ids:
            return set()

        stmt = select(LinkRelation.target_entity_id).where(
            (LinkRelation.source_entity_type == source_type)
            & (LinkRelation.source_entity_id == source_id)
            & (LinkRelation.target_entity_type == target_type)
            & (LinkRelation.target_entity_id.in_(target_ids))
        )
        result = await self.session.execute(stmt)
        return set(result.scalars().all())

    async def bulk_create(self, links: list[LinkRelation]) -> list[LinkRelation]:
        if not links:
            return []

        for link in links:
            link.created_by_id = self.auth_info.flow_user_id

        self.session.add_all(links)
        await self.session.flush(links)
        return links
