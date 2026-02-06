from __future__ import annotations

import uuid

from commons.db.v6.base import HasCreatedAt
from commons.db.v6.user.user import HasCreatedBy, User
from sqlalchemy import BigInteger, Boolean, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base_models import PyConnectPosBaseModel
from app.graphql.pos.data_exchange.models.enums import (
    ExchangeFileStatus,
    ValidationStatus,
)


class ExchangeFile(PyConnectPosBaseModel, HasCreatedBy, HasCreatedAt, kw_only=True):
    __tablename__ = "exchange_files"
    __table_args__ = (
        Index("ix_exchange_files_org_id", "org_id"),
        Index("ix_exchange_files_file_sha", "file_sha"),
        Index("ix_exchange_files_status", "status"),
        Index("ix_exchange_files_validation_status", "validation_status"),
        {"schema": "connect_pos", "extend_existing": True},
    )

    org_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    s3_key: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    file_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)
    row_count: Mapped[int] = mapped_column(nullable=False)
    reporting_period: Mapped[str] = mapped_column(String(100), nullable=False)
    is_pos: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_pot: Mapped[bool] = mapped_column(Boolean, nullable=False)

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ExchangeFileStatus.PENDING.value,
    )

    validation_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ValidationStatus.NOT_VALIDATED.value,
    )

    target_organizations: Mapped[list[ExchangeFileTargetOrg]] = relationship(
        "ExchangeFileTargetOrg",
        back_populates="exchange_file",
        cascade="all, delete-orphan",
        init=False,
    )
    created_by: Mapped[User] = relationship(init=False)

    @property
    def status_enum(self) -> ExchangeFileStatus:
        return ExchangeFileStatus(self.status)

    @property
    def validation_status_enum(self) -> ValidationStatus:
        return ValidationStatus(self.validation_status)


class ExchangeFileTargetOrg(PyConnectPosBaseModel, kw_only=True):
    __tablename__ = "exchange_file_target_orgs"
    __table_args__ = (
        Index("ix_exchange_file_target_orgs_file_id", "exchange_file_id"),
        Index("ix_exchange_file_target_orgs_org_id", "connected_org_id"),
        {"schema": "connect_pos", "extend_existing": True},
    )

    exchange_file_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("connect_pos.exchange_files.id", ondelete="CASCADE"),
        nullable=False,
        init=False,
    )
    connected_org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )

    exchange_file: Mapped[ExchangeFile] = relationship(
        "ExchangeFile",
        back_populates="target_organizations",
        init=False,
    )
