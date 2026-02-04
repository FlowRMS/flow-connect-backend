from decimal import Decimal
from typing import Any, cast

import strawberry
from commons.db.v6 import ShippingCarrier
from commons.db.v6.crm.shipping_carriers.shipping_carrier_model import CarrierType
from strawberry.scalars import JSON

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class ShippingCarrierInput(BaseInputGQL[ShippingCarrier]):
    """Input type for creating/updating shipping carriers."""

    name: str
    carrier_type: CarrierType | None = None
    code: str | None = None  # SCAC code
    account_number: str | None = None
    is_active: bool = True

    # Account & Billing
    # Note: billing_address is stored via Address model with source_type=SHIPPING_CARRIER
    payment_terms: str | None = None

    # API Integration
    api_key: str | None = None
    api_endpoint: str | None = None
    tracking_url_template: str | None = None

    # Contact Information - stored via Contact model with LinkRelation

    # Service Configuration
    service_types: JSON | None = None  # JSONB in database
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
            carrier_type=self.carrier_type,
            code=self.code,
            account_number=self.account_number,
            is_active=self.is_active,
            payment_terms=self.payment_terms,
            api_key=self.api_key,
            api_endpoint=self.api_endpoint,
            tracking_url_template=self.tracking_url_template,
            service_types=cast(dict[Any, Any], self.service_types)
            if self.service_types
            else None,
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
