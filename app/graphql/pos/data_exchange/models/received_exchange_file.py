from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.db.base_models import PyConnectPosBaseModel
from app.graphql.pos.data_exchange.models.enums import ReceivedExchangeFileStatus


class ReceivedExchangeFile(PyConnectPosBaseModel, kw_only=True):
    __tablename__ = "received_exchange_files"
    __table_args__ = (
        Index("ix_received_exchange_files_org_id", "org_id"),
        Index("ix_received_exchange_files_sender_org_id", "sender_org_id"),
        Index("ix_received_exchange_files_status", "status"),
        UniqueConstraint("s3_key", name="uq_received_exchange_files_s3_key"),
        {"schema": "connect_pos", "extend_existing": True},
    )

    org_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    sender_org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False
    )
    s3_key: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(nullable=False)
    file_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)
    row_count: Mapped[int] = mapped_column(nullable=False)
    reporting_period: Mapped[str] = mapped_column(String(100), nullable=False)
    is_pos: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_pot: Mapped[bool] = mapped_column(Boolean, nullable=False)

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ReceivedExchangeFileStatus.NEW.value,
    )

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=None,
    )

    @property
    def status_enum(self) -> ReceivedExchangeFileStatus:
        return ReceivedExchangeFileStatus(self.status)
