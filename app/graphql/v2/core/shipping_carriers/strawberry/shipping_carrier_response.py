"""Strawberry response types for shipping carriers."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Self, cast
from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6 import ShippingCarrier
from commons.db.v6.core.addresses.address import AddressSourceTypeEnum
from commons.db.v6.crm.links.entity_type import EntityType
from strawberry.scalars import JSON

from app.core.db.adapters.dto import DTOMixin
from app.graphql.addresses.repositories.address_repository import AddressRepository
from app.graphql.addresses.strawberry.address_response import AddressResponse
from app.graphql.contacts.repositories.contacts_repository import ContactsRepository
from app.graphql.contacts.strawberry.contact_response import ContactLiteResponse
from app.graphql.inject import inject
from app.graphql.links.repositories.link_relations_repository import (
    LinkRelationsRepository,
)

if TYPE_CHECKING:
    pass


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
    payment_terms: str | None

    # API Integration
    api_key: str | None
    api_endpoint: str | None
    tracking_url_template: str | None

    # Service Configuration
    service_types: JSON | None  # JSONB in database
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
            payment_terms=model.payment_terms,
            api_key=model.api_key,
            api_endpoint=model.api_endpoint,
            tracking_url_template=model.tracking_url_template,
            service_types=cast(JSON, model.service_types)
            if model.service_types
            else None,
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

    @strawberry.field
    @inject
    async def billing_address(
        self,
        address_repo: Injected[AddressRepository],
    ) -> AddressResponse | None:
        """Get the billing address for this shipping carrier."""
        addresses = await address_repo.list_by_source(
            source_type=AddressSourceTypeEnum.SHIPPING_CARRIER,
            source_id=self.id,
        )
        # Return the first (primary) billing address if exists
        if addresses:
            return AddressResponse.from_orm_model(addresses[0])
        return None

    @strawberry.field
    @inject
    async def primary_contact(
        self,
        link_repo: Injected[LinkRelationsRepository],
        contacts_repo: Injected[ContactsRepository],
    ) -> ContactLiteResponse | None:
        """Get the primary contact for this shipping carrier via LinkRelation."""
        # Find links from this carrier to contacts
        links = await link_repo.get_links_from_source(
            source_type=EntityType.SHIPPING_CARRIER,
            source_id=self.id,
        )

        # Filter for contact links and get the first one
        contact_links = [
            link for link in links if link.target_entity_type == EntityType.CONTACT
        ]

        if not contact_links:
            return None

        # Get the contact
        contact = await contacts_repo.get_by_id(contact_links[0].target_entity_id)
        if contact:
            return ContactLiteResponse.from_orm_model(contact)
        return None
