"""Repository for Note entity."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.links.models.entity_type import EntityType
from app.graphql.links.models.link_relation_model import LinkRelation
from app.graphql.notes.models.note_model import Note


class NotesRepository(BaseRepository[Note]):
    """Repository for Notes entity."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, Note)

    async def find_by_entity(
        self,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> list[Note]:
        """Find all notes linked to a specific entity via link relations."""
        # First, get all link relations where:
        # - Source is NOTE and target is the given entity, OR
        # - Target is NOTE and source is the given entity
        links_stmt = select(LinkRelation).where(
            (
                (LinkRelation.source_entity_type == EntityType.NOTE)
                & (LinkRelation.target_entity_type == entity_type)
                & (LinkRelation.target_entity_id == entity_id)
            )
            | (
                (LinkRelation.target_entity_type == EntityType.NOTE)
                & (LinkRelation.source_entity_type == entity_type)
                & (LinkRelation.source_entity_id == entity_id)
            )
        )
        links_result = await self.session.execute(links_stmt)
        links = list(links_result.scalars().all())

        if not links:
            return []

        # Extract note IDs from the links
        note_ids: list[UUID] = []
        for link in links:
            if link.source_entity_type == EntityType.NOTE:
                note_ids.append(link.source_entity_id)
            elif link.target_entity_type == EntityType.NOTE:
                note_ids.append(link.target_entity_id)

        # Query notes with those IDs
        notes_stmt = select(Note).where(Note.id.in_(note_ids))
        notes_result = await self.session.execute(notes_stmt)
        return list(notes_result.scalars().all())
