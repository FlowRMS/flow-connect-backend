"""SQLAlchemy ORM model for ManufacturerOrder entity."""

import uuid

from sqlalchemy import Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import CrmBaseModel


class ManufacturerOrder(CrmBaseModel, kw_only=True):
    """
    ManufacturerOrder entity storing the display order of manufacturers.

    This table stores the sort order for manufacturers (factories) in the spec sheets view.
    """

    __tablename__ = "manufacturer_order"
    __table_args__ = (
        UniqueConstraint("factory_id", name="uq_manufacturer_order_factory_id"),
        {"schema": "pycrm"},
    )

    factory_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        """String representation of the ManufacturerOrder."""
        return f"<ManufacturerOrder(id={self.id}, factory_id={self.factory_id}, sort_order={self.sort_order})>"
