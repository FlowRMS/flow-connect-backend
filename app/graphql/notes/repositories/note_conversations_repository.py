"""Repository for NoteConversation entity."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.notes.models.note_conversation_model import NoteConversation


class NoteConversationsRepository(BaseRepository[NoteConversation]):
    """Repository for NoteConversations entity."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, NoteConversation)

    async def get_by_note_id(self, note_id: UUID) -> list[NoteConversation]:
        """Get all conversations for a specific note."""
        stmt = select(NoteConversation).where(NoteConversation.note_id == note_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
