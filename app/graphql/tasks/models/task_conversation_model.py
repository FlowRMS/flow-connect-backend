"""Task conversation model for threaded comments on tasks."""

from uuid import UUID

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import CrmBaseModel, HasCreatedAt, HasCreatedBy
from app.graphql.tasks.models.task_model import Task


class TaskConversation(CrmBaseModel, HasCreatedAt, HasCreatedBy, kw_only=True):
    """Task conversation entity for threaded comments on tasks."""

    __tablename__ = "task_conversations"

    task_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(Task.id),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    task: Mapped[Task] = relationship(init=False, back_populates="conversations")
