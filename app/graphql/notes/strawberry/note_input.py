"""GraphQL input types for notes."""

from uuid import UUID

import strawberry

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.notes.models.note_conversation_model import NoteConversation
from app.graphql.notes.models.note_model import Note


@strawberry.input
class NoteInput(BaseInputGQL[Note]):
    """GraphQL input type for creating/updating notes."""

    title: str
    content: str
    tags: list[str] | None = strawberry.UNSET
    mentions: list[UUID] | None = strawberry.UNSET

    def to_orm_model(self) -> Note:
        """Convert input to ORM model."""
        return Note(
            title=self.title,
            content=self.content,
            tags=self.optional_field(self.tags),
            mentions=self.optional_field(self.mentions),
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
