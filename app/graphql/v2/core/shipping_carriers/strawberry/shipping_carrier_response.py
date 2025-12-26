"""Strawberry response types for shipping carriers."""

from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry

from commons.db.v6 import ShippingCarrier

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class ShippingCarrierResponse(DTOMixin[ShippingCarrier]):
    """Response type for shipping carriers."""

    _instance: strawberry.Private[ShippingCarrier]
    id: UUID
    name: str
    code: str | None  # SCAC code
    account_number: str | None
    is_active: bool | None
    created_at: datetime

    # Account & Billing
    billing_address: str | None
    payment_terms: str | None

    # API Integration
    api_key: str | None
    api_endpoint: str | None
    tracking_url_template: str | None

    # Contact Information
    contact_name: str | None
    contact_phone: str | None
    contact_email: str | None

    # Service Configuration
    service_types: list[str] | None
    default_service_type: str | None

    # Shipping Settings - using Decimal
    max_weight: Decimal | None
    max_dimensions: str | None
    residential_surcharge: Decimal | None
    fuel_surcharge_percent: Decimal | None

    # Pickup Settings
    pickup_schedule: str | None
    pickup_location: str | None

    # Notes
    remarks: str | None
    internal_notes: str | None

    @classmethod
    def from_orm_model(cls, model: ShippingCarrier) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            name=model.name,
            code=model.code,
            account_number=model.account_number,
            is_active=model.is_active,
            created_at=model.created_at,
            billing_address=model.billing_address,
            payment_terms=model.payment_terms,
            api_key=model.api_key,
            api_endpoint=model.api_endpoint,
            tracking_url_template=model.tracking_url_template,
            contact_name=model.contact_name,
            contact_phone=model.contact_phone,
            contact_email=model.contact_email,
            service_types=model.service_types,
            default_service_type=model.default_service_type,
            max_weight=model.max_weight,
            max_dimensions=model.max_dimensions,
            residential_surcharge=model.residential_surcharge,
            fuel_surcharge_percent=model.fuel_surcharge_percent,
            pickup_schedule=model.pickup_schedule,
            pickup_location=model.pickup_location,
            remarks=model.remarks,
            internal_notes=model.internal_notes,
        )
