"""Strawberry input types for shipping carriers."""

from decimal import Decimal

import strawberry

from commons.db.v6 import ShippingCarrier

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class ShippingCarrierInput(BaseInputGQL[ShippingCarrier]):
    """Input type for creating/updating shipping carriers."""

    name: str
    code: str | None = None  # SCAC code
    account_number: str | None = None
    is_active: bool = True

    # Account & Billing
    billing_address: str | None = None
    payment_terms: str | None = None

    # API Integration
    api_key: str | None = None
    api_endpoint: str | None = None
    tracking_url_template: str | None = None

    # Contact Information
    contact_name: str | None = None
    contact_phone: str | None = None
    contact_email: str | None = None

    # Service Configuration
    service_types: list[str] | None = None
    default_service_type: str | None = None

    # Shipping Settings - using Decimal
    max_weight: Decimal | None = None
    max_dimensions: str | None = None
    residential_surcharge: Decimal | None = None
    fuel_surcharge_percent: Decimal | None = None

    # Pickup Settings
    pickup_schedule: str | None = None
    pickup_location: str | None = None

    # Notes
    remarks: str | None = None
    internal_notes: str | None = None

    def to_orm_model(self) -> ShippingCarrier:
        return ShippingCarrier(
            name=self.name,
            code=self.code,
            account_number=self.account_number,
            is_active=self.is_active,
            billing_address=self.billing_address,
            payment_terms=self.payment_terms,
            api_key=self.api_key,
            api_endpoint=self.api_endpoint,
            tracking_url_template=self.tracking_url_template,
            contact_name=self.contact_name,
            contact_phone=self.contact_phone,
            contact_email=self.contact_email,
            service_types=self.service_types,
            default_service_type=self.default_service_type,
            max_weight=self.max_weight,
            max_dimensions=self.max_dimensions,
            residential_surcharge=self.residential_surcharge,
            fuel_surcharge_percent=self.fuel_surcharge_percent,
            pickup_schedule=self.pickup_schedule,
            pickup_location=self.pickup_location,
            remarks=self.remarks,
            internal_notes=self.internal_notes,
        )
