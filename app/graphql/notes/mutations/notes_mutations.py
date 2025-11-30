"""GraphQL mutations for Notes entity."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.notes.services.notes_service import NotesService
from app.graphql.notes.strawberry.note_input import (
    NoteConversationInput,
    NoteInput,
)
from app.graphql.notes.strawberry.note_response import (
    NoteConversationType,
    NoteType,
)


@strawberry.type
class NotesMutations:
    """GraphQL mutations for Notes entity."""

    @strawberry.mutation
    @inject
    async def create_note(
        self,
        input: NoteInput,
        service: Injected[NotesService],
    ) -> NoteType:
        """Create a new note."""
        return NoteType.from_orm_model(await service.create_note(note_input=input))

    @strawberry.mutation
    @inject
    async def update_note(
        self,
        id: UUID,
        input: NoteInput,
        service: Injected[NotesService],
    ) -> NoteType:
        """Update an existing note."""
        return NoteType.from_orm_model(await service.update_note(id, input))

    @strawberry.mutation
    @inject
    async def delete_note(
        self,
        id: UUID,
        service: Injected[NotesService],
    ) -> bool:
        """Delete a note by ID."""
        return await service.delete_note(note_id=id)

    @strawberry.mutation
    @inject
    async def add_note_conversation(
        self,
        input: NoteConversationInput,
        service: Injected[NotesService],
    ) -> NoteConversationType:
        """Add a conversation entry to a note."""
        return NoteConversationType.from_orm_model(
            await service.add_conversation(conversation_input=input)
        )

    @strawberry.mutation
    @inject
    async def update_note_conversation(
        self,
        input: NoteConversationInput,
        service: Injected[NotesService],
    ) -> NoteConversationType:
        """Update an existing conversation entry."""
        return NoteConversationType.from_orm_model(
            await service.update_conversation(conversation_input=input)
        )

    @strawberry.mutation
    @inject
    async def delete_note_conversations(
        self,
        note_id: UUID,
        service: Injected[NotesService],
    ) -> bool:
        """Delete a conversation entry by ID."""
        return await service.delete_conversation(note_id=note_id)
