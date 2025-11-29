"""SQLAlchemy declarative base for all ORM models."""

import datetime
import uuid

from commons.db.models.base import BaseModel
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column


class CrmBaseModel(BaseModel):
    __abstract__ = True
    __table_args__ = {"schema": "crm"}


class HasCreatedAt(MappedAsDataclass):
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        init=False,
        server_default=func.now(),  # Corrected line
    )


class HasCreatedBy(MappedAsDataclass):
    created_by: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        init=False,
        nullable=False,
    )
