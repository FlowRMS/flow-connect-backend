"""Note conversation model for threaded comments on notes."""

from uuid import UUID

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import BaseModel, HasCreatedAt, HasCreatedBy
from app.graphql.notes.models.note_model import Note


class NoteConversation(BaseModel, HasCreatedAt, HasCreatedBy, kw_only=True):
    """Note conversation entity for threaded comments on notes."""

    __tablename__ = "note_conversations"

    note_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(Note.id),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    note: Mapped[Note] = relationship(init=False, back_populates="conversations")
