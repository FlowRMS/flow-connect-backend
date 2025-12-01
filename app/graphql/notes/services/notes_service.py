"""Service for Notes entity business logic."""

from uuid import UUID

from commons.auth import AuthInfo

from app.errors.common_errors import NotFoundError
from app.graphql.links.models.entity_type import EntityType
from app.graphql.notes.models.note_conversation_model import NoteConversation
from app.graphql.notes.models.note_model import Note
from app.graphql.notes.repositories.note_conversations_repository import (
    NoteConversationsRepository,
)
from app.graphql.notes.repositories.notes_repository import NotesRepository
from app.graphql.notes.strawberry.note_input import (
    NoteConversationInput,
    NoteInput,
)


class NotesService:
    """Service for Notes entity business logic."""

    def __init__(
        self,
        repository: NotesRepository,
        conversations_repository: NoteConversationsRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.conversations_repository = conversations_repository
        self.auth_info = auth_info

    async def create_note(self, note_input: NoteInput) -> Note:
        """Create a new note."""
        note = note_input.to_orm_model()
        return await self.repository.create(note)

    async def update_note(self, note_id: UUID, note_input: NoteInput) -> Note:
        """Update an existing note."""
        if not await self.repository.exists(note_id):
            raise NotFoundError(str(note_id))

        note = note_input.to_orm_model()
        note.id = note_id
        return await self.repository.update(note)

    async def delete_note(self, note_id: UUID | str) -> bool:
        """Delete a note by ID."""
        if not await self.repository.exists(note_id):
            raise NotFoundError(str(note_id))
        return await self.repository.delete(note_id)

    async def get_note(self, note_id: UUID | str) -> Note:
        """Get a note by ID."""
        note = await self.repository.get_by_id(note_id)
        if not note:
            raise NotFoundError(str(note_id))
        return note

    async def list_notes(self, limit: int = 20, offset: int = 0) -> list[Note]:
        """List notes with pagination."""
        return await self.repository.list_all(limit=limit, offset=offset)

    async def find_notes_by_entity(
        self, entity_type: EntityType, entity_id: UUID
    ) -> list[Note]:
        """Find all notes linked to a specific entity."""
        return await self.repository.find_by_entity(entity_type, entity_id)

    async def add_conversation(
        self, conversation_input: NoteConversationInput
    ) -> NoteConversation:
        """Add a conversation entry to a note."""
        if not await self.repository.exists(conversation_input.note_id):
            raise NotFoundError(str(conversation_input.note_id))
        return await self.conversations_repository.create(
            conversation_input.to_orm_model()
        )

    async def update_conversation(
        self, conversation_id: UUID, conversation_input: NoteConversationInput
    ) -> NoteConversation:
        """Update an existing conversation entry."""
        if not await self.conversations_repository.exists(conversation_id):
            raise NotFoundError(str(conversation_id))
        conversation = conversation_input.to_orm_model()
        conversation.id = conversation_id
        return await self.conversations_repository.update(conversation)

    async def delete_conversation(self, conversation_id: UUID | str) -> bool:
        """Delete a single conversation entry by its ID."""
        if not await self.conversations_repository.exists(conversation_id):
            raise NotFoundError(str(conversation_id))
        return await self.conversations_repository.delete(conversation_id)

    async def delete_conversations(self, note_id: UUID) -> bool:
        if not await self.repository.exists(note_id):
            raise NotFoundError(str(note_id))
        return await self.conversations_repository.delete_by_note_id(note_id)

    async def get_conversations_by_note(self, note_id: UUID) -> list[NoteConversation]:
        """Get all conversation entries for a specific note."""
        if not await self.repository.exists(note_id):
            raise NotFoundError(str(note_id))
        return await self.conversations_repository.get_by_note_id(note_id)
