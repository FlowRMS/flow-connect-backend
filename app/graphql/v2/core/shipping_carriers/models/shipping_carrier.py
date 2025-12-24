"""SQLAlchemy model for shipping carriers."""

from datetime import datetime
from typing import Any

from commons.db.v6.models import BaseModel
from sqlalchemy import Boolean, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column


class ShippingCarrier(BaseModel):
    """Shipping carrier model representing pycrm.shipping_carriers table."""

    __tablename__ = "shipping_carriers"
    __table_args__ = {"schema": "pycrm", "extend_existing": True}

    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str | None] = mapped_column(String(50), nullable=True, default=None)
    account_number: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, default=None
    )

    # Account & Billing
    billing_address: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    payment_terms: Mapped[str | None] = mapped_column(String(50), nullable=True, default=None)

    # API Integration
    api_key: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    api_endpoint: Mapped[str | None] = mapped_column(String(500), nullable=True, default=None)
    tracking_url_template: Mapped[str | None] = mapped_column(String(500), nullable=True, default=None)

    # Contact Information
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True, default=None)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)

    # Service Configuration
    service_types: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True, default=None)
    default_service_type: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None)

    # Shipping Settings
    max_weight: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True, default=None)
    max_dimensions: Mapped[str | None] = mapped_column(String(50), nullable=True, default=None)
    residential_surcharge: Mapped[float | None] = mapped_column(
        Numeric(10, 2), nullable=True, default=None
    )
    fuel_surcharge_percent: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True, default=None
    )

    # Pickup Settings
    pickup_schedule: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    pickup_location: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)

    # Notes
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    internal_notes: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
