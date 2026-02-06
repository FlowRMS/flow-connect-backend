import uuid
from datetime import datetime

from commons.db.v6.base import HasCreatedAt
from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.db.base_models import PyConnectPosBaseModel


class OrganizationPreference(PyConnectPosBaseModel, HasCreatedAt, kw_only=True):
    __tablename__ = "organization_preferences"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "application",
            "preference_key",
            name="uq_org_preferences_org_application_key",
        ),
        {"schema": "connect_pos", "extend_existing": True},
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True))
    application: Mapped[str] = mapped_column(String(50))
    preference_key: Mapped[str] = mapped_column(String(50))
    preference_value: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        init=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
