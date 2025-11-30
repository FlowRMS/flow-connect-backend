"""Note model for the CRM system."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ARRAY, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import CrmBaseModel, HasCreatedAt, HasCreatedBy

if TYPE_CHECKING:
    from app.graphql.notes.models.note_conversation_model import NoteConversation


class Note(CrmBaseModel, HasCreatedAt, HasCreatedBy, kw_only=True):
    """Note entity representing a note in the CRM system."""

    __tablename__ = "notes"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    mentions: Mapped[list[UUID] | None] = mapped_column(
        ARRAY(PG_UUID(as_uuid=True)), nullable=True
    )

    conversations: Mapped[list["NoteConversation"]] = relationship(
        init=False, back_populates="note", cascade="all, delete, delete-orphan"
    )
