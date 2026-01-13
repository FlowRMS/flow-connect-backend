"""GraphQL input types for notes."""

from uuid import UUID

import strawberry
from commons.db.v6.crm.notes.note_conversation_model import NoteConversation
from commons.db.v6.crm.notes.note_model import Note

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class NoteInput(BaseInputGQL[Note]):
    """GraphQL input type for creating/updating notes."""

    title: str
    content: str
    tags: list[str] | None = strawberry.UNSET
    mentions: list[UUID] | None = strawberry.UNSET
    is_public: bool = False

    def to_orm_model(self) -> Note:
        """Convert input to ORM model."""
        return Note(
            title=self.title,
            content=self.content,
            tags=self.optional_field(self.tags),
            mentions=self.optional_field(self.mentions),
            is_public=self.is_public,
        )


@strawberry.input
class NoteConversationInput(BaseInputGQL[NoteConversation]):
    """GraphQL input type for creating/updating note conversations."""

    note_id: UUID
    content: str

    def to_orm_model(self) -> NoteConversation:
        return NoteConversation(
            note_id=self.note_id,
            content=self.content,
        )
