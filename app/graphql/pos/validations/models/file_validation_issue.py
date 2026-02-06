from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from commons.db.v6.base import HasCreatedAt
from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base_models import PyConnectPosBaseModel

if TYPE_CHECKING:
    from app.graphql.pos.data_exchange.models.exchange_file import ExchangeFile


class FileValidationIssue(PyConnectPosBaseModel, HasCreatedAt, kw_only=True):
    __tablename__ = "file_validation_issues"
    __table_args__ = (
        Index("ix_file_validation_issues_exchange_file_id", "exchange_file_id"),
        {"schema": "connect_pos", "extend_existing": True},
    )

    exchange_file_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("connect_pos.exchange_files.id", ondelete="CASCADE"),
        nullable=False,
    )
    row_number: Mapped[int] = mapped_column(nullable=False)
    column_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    validation_key: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    row_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True, default=None
    )

    exchange_file: Mapped[ExchangeFile] = relationship(
        "ExchangeFile",
        init=False,
    )
