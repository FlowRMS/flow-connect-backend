"""SQLAlchemy models for warehouse settings."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from commons.db.v6.models import BaseModel
from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.graphql.v2.core.warehouses.models.warehouse_location import (
        WarehouseLocation,
    )


class Warehouse(BaseModel):
    """Warehouse model representing pycrm.warehouses table."""

    __tablename__ = "warehouses"
    __table_args__ = {"schema": "pycrm", "extend_existing": True}

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    address_line: Mapped[str | None] = mapped_column(String(500), nullable=True, default=None)
    address_line_2: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None)
    zip: Mapped[str | None] = mapped_column(String(20), nullable=True, default=None)
    country: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True, default=None)
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True, default=None)
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, default=None, init=False
    )

    # Relationships
    members: Mapped[list["WarehouseMember"]] = relationship(
        "WarehouseMember", back_populates="warehouse", lazy="selectin", default_factory=list
    )
    settings: Mapped["WarehouseSettings | None"] = relationship(
        "WarehouseSettings", back_populates="warehouse", uselist=False, lazy="selectin", default=None
    )
    structure: Mapped[list["WarehouseStructure"]] = relationship(
        "WarehouseStructure", back_populates="warehouse", lazy="selectin", default_factory=list
    )
    locations: Mapped[list["WarehouseLocation"]] = relationship(
        "WarehouseLocation", back_populates="warehouse", lazy="selectin", default_factory=list
    )


class WarehouseMember(BaseModel):
    """Warehouse member model representing pycrm.warehouse_members table."""

    __tablename__ = "warehouse_members"
    __table_args__ = {"schema": "pycrm", "extend_existing": True}

    warehouse_id: Mapped[UUID] = mapped_column(
        ForeignKey("pycrm.warehouses.id"), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(nullable=False)
    role: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)  # 1=worker, 2=manager
    role_name: Mapped[str | None] = mapped_column(String(20), nullable=True, default=None)
    created_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, default=None
    )
    created_by_id: Mapped[UUID | None] = mapped_column(nullable=True, default=None)

    # Relationships
    warehouse: Mapped["Warehouse"] = relationship(
        "Warehouse", back_populates="members", default=None
    )


class WarehouseSettings(BaseModel):
    """Warehouse settings model representing pycrm.warehouse_settings table."""

    __tablename__ = "warehouse_settings"
    __table_args__ = {"schema": "pycrm", "extend_existing": True}

    warehouse_id: Mapped[UUID] = mapped_column(
        ForeignKey("pycrm.warehouses.id"), unique=True, nullable=False
    )
    auto_generate_codes: Mapped[bool] = mapped_column(Boolean, default=False)
    require_location: Mapped[bool] = mapped_column(Boolean, default=True)
    show_in_pick_lists: Mapped[bool] = mapped_column(Boolean, default=True)
    generate_qr_codes: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    warehouse: Mapped["Warehouse"] = relationship(
        "Warehouse", back_populates="settings", default=None
    )


class WarehouseStructure(BaseModel):
    """Warehouse structure model for location level configuration.

    Represents pycrm.warehouse_structure table - stores which location
    levels are enabled for a warehouse (section, aisle, shelf, etc.).
    """

    __tablename__ = "warehouse_structure"
    __table_args__ = {"schema": "pycrm", "extend_existing": True}

    warehouse_id: Mapped[UUID] = mapped_column(
        ForeignKey("pycrm.warehouses.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # 'section', 'aisle', etc.
    level_order: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    warehouse: Mapped["Warehouse"] = relationship(
        "Warehouse", back_populates="structure", default=None
    )
