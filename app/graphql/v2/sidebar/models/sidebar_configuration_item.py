from __future__ import annotations

from uuid import UUID

from commons.db.v6 import PyCRMBaseModel
from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.graphql.v2.sidebar.models.sidebar_configuration import SidebarConfiguration


class SidebarConfigurationItem(PyCRMBaseModel, kw_only=True):
    __tablename__ = "sidebar_configuration_items"
    __table_args__ = (
        UniqueConstraint("configuration_id", "item_id", name="uq_sidebar_config_item"),
        {"schema": "pycrm", "extend_existing": True},
    )

    configuration_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(SidebarConfiguration.id, ondelete="CASCADE"),
        nullable=False,
        init=False,
    )
    group_id: Mapped[str] = mapped_column(String(50), nullable=False)
    item_id: Mapped[str] = mapped_column(String(50), nullable=False)
    item_order: Mapped[int] = mapped_column(Integer, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    configuration: Mapped[SidebarConfiguration] = relationship(
        back_populates="items",
        init=False,
        lazy="noload",
    )
