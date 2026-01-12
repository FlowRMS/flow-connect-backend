from __future__ import annotations

import datetime
from uuid import UUID

from commons.db.int_enum import IntEnum
from commons.db.v6 import PyCRMBaseModel, RbacRoleEnum, User
from sqlalchemy import ForeignKey, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.graphql.v2.sidebar.models.sidebar_configuration import SidebarConfiguration


class RoleSidebarAssignment(PyCRMBaseModel, kw_only=True):
    __tablename__ = "role_sidebar_assignments"

    role: Mapped[RbacRoleEnum] = mapped_column(
        IntEnum(RbacRoleEnum),
        nullable=False,
        unique=True,
    )
    configuration_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(SidebarConfiguration.id, ondelete="CASCADE"),
        nullable=False,
    )
    assigned_by_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(User.id),
        nullable=False,
    )
    assigned_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        init=False,
        server_default=func.now(),
    )

    configuration: Mapped[SidebarConfiguration] = relationship(
        init=False,
        lazy="joined",
    )
