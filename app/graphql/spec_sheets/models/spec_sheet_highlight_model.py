"""SQLAlchemy ORM models for SpecSheet Highlights."""

import uuid

from commons.db.models import User
from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import CrmBaseModel, HasCreatedAt, HasCreatedBy


class SpecSheetHighlightVersion(CrmBaseModel, HasCreatedAt, HasCreatedBy, kw_only=True):
    """
    SpecSheetHighlightVersion entity representing a saved version of highlights on a spec sheet.

    Each version contains multiple highlight regions and can have a name/label.
    """

    __tablename__ = "spec_sheet_highlight_versions"

    # Reference to the spec sheet
    spec_sheet_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("pycrm.spec_sheets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Version metadata
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, default="Default Highlights"
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    regions: Mapped[list["SpecSheetHighlightRegion"]] = relationship(
        "SpecSheetHighlightRegion",
        back_populates="version",
        cascade="all, delete-orphan",
        lazy="selectin",
        init=False,
    )
    created_by: Mapped[User] = relationship(init=False, lazy="joined")

    def __repr__(self) -> str:
        """String representation."""
        return f"<SpecSheetHighlightVersion(id={self.id}, name='{self.name}', version={self.version_number})>"


class SpecSheetHighlightRegion(CrmBaseModel, HasCreatedAt, kw_only=True):
    """
    SpecSheetHighlightRegion entity representing a single highlight region on a PDF page.

    Stores the shape, position, color, and other properties of a highlight.
    """

    __tablename__ = "spec_sheet_highlight_regions"

    # Reference to the version
    version_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("pycrm.spec_sheet_highlight_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Page information
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Position and size (stored as percentages 0-100 for zoom independence)
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)
    width: Mapped[float] = mapped_column(Float, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)

    # Shape properties
    shape_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'rectangle', 'oval', 'highlight'
    color: Mapped[str] = mapped_column(String(20), nullable=False)  # hex color

    # Optional annotation/note
    annotation: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)

    # Relationships
    version: Mapped["SpecSheetHighlightVersion"] = relationship(
        "SpecSheetHighlightVersion", back_populates="regions", init=False
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<SpecSheetHighlightRegion(id={self.id}, page={self.page_number}, shape='{self.shape_type}')>"
