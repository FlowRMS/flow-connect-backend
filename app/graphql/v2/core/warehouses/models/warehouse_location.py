"""SQLAlchemy model for warehouse locations."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from commons.db.v6.models import BaseModel
from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.graphql.v2.core.warehouses.models.warehouse import Warehouse


class WarehouseLocation(BaseModel):
    """Warehouse location model for hierarchical storage locations.

    Represents pycrm.warehouse_locations table - stores actual location
    instances (Section A, Aisle 3, Bin B-12) with hierarchy via parent_id.
    """

    __tablename__ = "warehouse_locations"
    __table_args__ = {"schema": "pycrm", "extend_existing": True}

    # Required fields first (no defaults)
    warehouse_id: Mapped[UUID] = mapped_column(
        ForeignKey("pycrm.warehouses.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # section, aisle, shelf, bay, row, bin

    # Optional fields (with defaults)
    parent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("pycrm.warehouse_locations.id", ondelete="CASCADE"), nullable=True, default=None
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)

    # Visual properties for layout
    x: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True, default=None)
    y: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True, default=None)
    width: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True, default=None)
    height: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True, default=None)
    rotation: Mapped[float | None] = mapped_column(
        Numeric(5, 2), default=0, nullable=True
    )

    created_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, default=None
    )

    # Relationships
    warehouse: Mapped["Warehouse"] = relationship(
        "Warehouse", back_populates="locations", default=None
    )
    parent: Mapped["WarehouseLocation | None"] = relationship(
        "WarehouseLocation",
        remote_side="WarehouseLocation.id",
        back_populates="children",
        default=None,
    )
    children: Mapped[list["WarehouseLocation"]] = relationship(
        "WarehouseLocation", back_populates="parent", lazy="selectin", default_factory=list
    )
