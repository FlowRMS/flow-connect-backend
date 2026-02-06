from __future__ import annotations

import uuid

from commons.db.v6.base import HasCreatedAt
from commons.db.v6.user.user import HasCreatedBy, User
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base_models import PyConnectPosBaseModel


class OrganizationAlias(
    PyConnectPosBaseModel, HasCreatedBy, HasCreatedAt, kw_only=True
):
    __tablename__ = "organization_aliases"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "connected_org_id",
            name="uq_organization_aliases_org_connected",
        ),
        {"schema": "connect_pos", "extend_existing": True},
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    connected_org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    alias: Mapped[str] = mapped_column(String(255), nullable=False)

    created_by: Mapped[User] = relationship(init=False)
