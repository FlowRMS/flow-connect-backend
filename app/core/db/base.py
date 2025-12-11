"""SQLAlchemy declarative base for all ORM models."""

import datetime
import uuid

from commons.db.models import User
from commons.db.models.base import BaseModel
from sqlalchemy import ForeignKey, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column


class CrmBaseModel(BaseModel):
    __abstract__ = True
    __table_args__ = {"schema": "pycrm"}


class HasCreatedAt(MappedAsDataclass):
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        init=False,
        server_default=func.now(),  # Corrected line
    )


class HasCreatedBy(MappedAsDataclass):
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("user.users.id"),  # Explicitly reference user schema
        init=False,
        nullable=False,
    )
