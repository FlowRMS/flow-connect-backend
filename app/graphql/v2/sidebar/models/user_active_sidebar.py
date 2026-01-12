from __future__ import annotations

from uuid import UUID

from commons.db.v6 import PyCRMBaseModel, User
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.graphql.v2.sidebar.models.sidebar_configuration import SidebarConfiguration


class UserActiveSidebar(PyCRMBaseModel, kw_only=True):
    __tablename__ = "user_active_sidebar"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(User.id, ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    configuration_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(SidebarConfiguration.id, ondelete="SET NULL"),
        nullable=True,
    )

    configuration: Mapped[SidebarConfiguration | None] = relationship(
        init=False,
        lazy="joined",
    )
