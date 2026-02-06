from __future__ import annotations

import uuid

from commons.db.v6.base import HasCreatedAt
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base_models import PyConnectPosBaseModel
from app.graphql.geography.models.geography import Subdivision


class ConnectionTerritory(PyConnectPosBaseModel, HasCreatedAt, kw_only=True):
    __tablename__ = "connection_territories"
    __table_args__ = (
        UniqueConstraint(
            "connection_id",
            "subdivision_id",
            name="uq_connection_territory",
        ),
        {"schema": "connect_pos", "extend_existing": True},
    )

    connection_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    subdivision_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("connect_geography.subdivisions.id", ondelete="CASCADE"),
        nullable=False,
    )

    subdivision: Mapped[Subdivision] = relationship(
        "Subdivision",
        init=False,
    )
