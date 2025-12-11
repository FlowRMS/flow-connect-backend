"""SQLAlchemy ORM model for SpecSheet entity."""

import uuid
from datetime import datetime
from uuid import UUID

from commons.db.models import Factory, User
from sqlalchemy import ARRAY, BigInteger, Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import CrmBaseModel, HasCreatedAt, HasCreatedBy


class SpecSheet(CrmBaseModel, HasCreatedAt, HasCreatedBy, kw_only=True):
    """
    SpecSheet entity representing a specification sheet/cut sheet in the CRM system.

    Spec sheets store manufacturer product specifications with metadata and categorization.
    """

    __tablename__ = "spec_sheets"

    # Basic Information
    manufacturer_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Upload Information
    upload_source: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'url' or 'file'
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_url: Mapped[str] = mapped_column(Text, nullable=False)

    # File Metadata
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Categorization
    categories: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    # Fields with defaults must come after fields without defaults
    page_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    needs_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    highlight_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    created_by: Mapped[User] = relationship(init=False, lazy="joined")

    def __repr__(self) -> str:
        """String representation of the SpecSheet."""
        return f"<SpecSheet(id={self.id}, display_name='{self.display_name}', manufacturer_id={self.manufacturer_id})>"
