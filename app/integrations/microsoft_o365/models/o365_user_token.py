"""Microsoft O365 user token model for storing OAuth tokens."""

import datetime
import uuid
from typing import TYPE_CHECKING

from commons.db.models import User
from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import CrmBaseModel, HasCreatedAt

if TYPE_CHECKING:
    pass


class O365UserToken(CrmBaseModel, HasCreatedAt, kw_only=True):
    """Store OAuth tokens for Microsoft O365 integration per user."""

    __tablename__ = "o365_user_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(User.id, ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Microsoft identity
    microsoft_user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )  # OID from MS token
    microsoft_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )  # UPN/email from MS

    # OAuth tokens
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str] = mapped_column(Text, nullable=False)

    # Token metadata
    expires_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )
    scope: Mapped[str] = mapped_column(Text, nullable=False)  # Space-separated scopes

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_used_at: Mapped[datetime.datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        default=None,
    )
    token_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Bearer",
    )

    # Relationship
    user: Mapped[User] = relationship(init=False, lazy="joined")
