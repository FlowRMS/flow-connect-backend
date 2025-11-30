"""GraphQL queries for Notes entity."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.links.models.entity_type import EntityType
from app.graphql.notes.services.notes_service import NotesService
from app.graphql.notes.strawberry.note_response import (
    NoteConversationType,
    NoteType,
)


@strawberry.type
class NotesQueries:
    """GraphQL queries for Notes entity."""

    @strawberry.field
    @inject
    async def note(
        self,
        id: UUID,
        service: Injected[NotesService],
    ) -> NoteType:
        """Get a note by ID."""
        return NoteType.from_orm_model(await service.get_note(id))

    @strawberry.field
    @inject
    async def notes(
        self,
        service: Injected[NotesService],
        limit: int = 20,
        offset: int = 0,
    ) -> list[NoteType]:
        """List notes with pagination."""
        notes = await service.list_notes(limit=limit, offset=offset)
        return [NoteType.from_orm_model(note) for note in notes]

    @strawberry.field
    @inject
    async def notes_by_entity(
        self,
        entity_type: EntityType,
        entity_id: UUID,
        service: Injected[NotesService],
    ) -> list[NoteType]:
        """Find all notes linked to a specific entity."""
        notes = await service.find_notes_by_entity(entity_type, entity_id)
        return [NoteType.from_orm_model(note) for note in notes]

    @strawberry.field
    @inject
    async def note_conversations(
        self,
        note_id: UUID,
        service: Injected[NotesService],
    ) -> list[NoteConversationType]:
        """Get all conversation entries for a specific note."""
        conversations = await service.get_conversations_by_note(note_id)
        return [
            NoteConversationType.from_orm_model(conversation)
            for conversation in conversations
        ]
