"""GraphQL output types for notes."""

from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.notes.models.note_conversation_model import NoteConversation
from app.graphql.notes.models.note_model import Note


@strawberry.type
class NoteConversationType(DTOMixin[NoteConversation]):
    id: UUID
    created_at: datetime
    created_by: UUID
    note_id: UUID
    content: str

    @classmethod
    def from_orm_model(cls, model: NoteConversation) -> Self:
        return cls(
            id=model.id,
            created_at=model.created_at,
            created_by=model.created_by,
            note_id=model.note_id,
            content=model.content,
        )


@strawberry.type
class NoteType(DTOMixin[Note]):
    _instance: strawberry.Private[Note]
    id: UUID
    created_at: datetime
    created_by: UUID
    title: str
    content: str
    tags: list[str] | None
    mentions: list[UUID] | None

    @classmethod
    def from_orm_model(cls, model: Note) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            created_at=model.created_at,
            created_by=model.created_by,
            title=model.title,
            content=model.content,
            tags=model.tags,
            mentions=model.mentions,
        )

    @strawberry.field
    def conversations(self) -> list[NoteConversationType]:
        return NoteConversationType.from_orm_model_list(self._instance.conversations)
