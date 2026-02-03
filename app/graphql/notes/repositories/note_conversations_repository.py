from uuid import UUID

from commons.db.v6.crm.notes.note_conversation_model import NoteConversation
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class NoteConversationsRepository(BaseRepository[NoteConversation]):
    """Repository for NoteConversations entity."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, NoteConversation)

    async def get_by_note_id(self, note_id: UUID) -> list[NoteConversation]:
        """Get all conversations for a specific note."""
        stmt = (
            select(NoteConversation)
            .options(joinedload(NoteConversation.created_by))
            .where(NoteConversation.note_id == note_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_note_id(self, note_id: UUID) -> bool:
        """Delete all conversations for a specific note.

        Args:
            note_id: The ID of the note whose conversations should be deleted.

        Returns:
            The number of conversations deleted.
        """
        note_conversations = await self.get_by_note_id(note_id)

        for conversation in note_conversations:
            _ = await self.delete(conversation.id)

        await self.session.flush()
        return True
