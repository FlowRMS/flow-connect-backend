from __future__ import annotations

import uuid

from commons.db.v6.base import HasCreatedAt
from commons.db.v6.user.user import HasCreatedBy, User
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base_models import PyConnectPosBaseModel


class PrefixPattern(PyConnectPosBaseModel, HasCreatedBy, HasCreatedAt, kw_only=True):
    __tablename__ = "prefix_patterns"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "name",
            name="uq_prefix_patterns_org_name",
        ),
        {"schema": "connect_pos", "extend_existing": True},
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_by: Mapped[User] = relationship(init=False)
