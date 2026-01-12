from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from commons.db.v6 import HasCreatedAt, PyCRMBaseModel, User
from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.graphql.v2.sidebar.models.sidebar_configuration_group import (
        SidebarConfigurationGroup,
    )
    from app.graphql.v2.sidebar.models.sidebar_configuration_item import (
        SidebarConfigurationItem,
    )


class SidebarConfiguration(PyCRMBaseModel, HasCreatedAt, kw_only=True):
    __tablename__ = "sidebar_configurations"
    __table_args__ = (
        UniqueConstraint(
            "owner_type", "owner_id", "name", name="uq_sidebar_config_owner_name"
        ),
        {"schema": "pycrm", "extend_existing": True},
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_type: Mapped[str] = mapped_column(String(10), nullable=False)
    owner_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )
    created_by_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(User.id),
        nullable=False,
    )
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        init=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    groups: Mapped[list["SidebarConfigurationGroup"]] = relationship(
        back_populates="configuration",
        init=False,
        lazy="noload",
        cascade="all, delete-orphan",
    )
    items: Mapped[list["SidebarConfigurationItem"]] = relationship(
        back_populates="configuration",
        init=False,
        lazy="noload",
        cascade="all, delete-orphan",
    )
