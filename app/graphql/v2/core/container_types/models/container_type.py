"""SQLAlchemy model for container types."""

from datetime import datetime

from commons.db.v6.models import BaseModel
from sqlalchemy import Integer, Numeric, String
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column


class ContainerType(BaseModel):
    """Container type model representing pycrm.container_types table."""

    __tablename__ = "container_types"
    __table_args__ = {"schema": "pycrm", "extend_existing": True}

    name: Mapped[str] = mapped_column(String, nullable=False)
    length: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)  # in inches
    width: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)  # in inches
    height: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)  # in inches
    weight: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False
    )  # tare weight in lbs
    order: Mapped[int] = mapped_column(Integer, nullable=False)  # display order
    created_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, default=None
    )
