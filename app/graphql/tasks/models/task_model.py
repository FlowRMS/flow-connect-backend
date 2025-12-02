from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from commons.db.int_enum import IntEnum
from commons.db.models import User
from sqlalchemy import ARRAY, Date, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import CrmBaseModel, HasCreatedAt, HasCreatedBy
from app.graphql.tasks.models.task_priority import TaskPriority
from app.graphql.tasks.models.task_status import TaskStatus

if TYPE_CHECKING:
    from app.graphql.tasks.models.task_conversation_model import TaskConversation


class Task(CrmBaseModel, HasCreatedAt, HasCreatedBy, kw_only=True):
    """Task entity representing a task in the CRM system."""

    __tablename__ = "tasks"

    # Required fields
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(IntEnum(TaskStatus), nullable=False)
    priority: Mapped[TaskPriority] = mapped_column(
        IntEnum(TaskPriority), nullable=False
    )

    # Optional fields
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_to_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    reminder_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    created_by: Mapped[User] = relationship(init=False, lazy="joined")
    conversations: Mapped[list["TaskConversation"]] = relationship(
        init=False, back_populates="task", cascade="all, delete, delete-orphan"
    )
