"""Strawberry response types for shipping carriers."""

from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6 import ShippingCarrier
from commons.db.v6.core.addresses.address import AddressSourceTypeEnum, AddressTypeEnum
from strawberry.scalars import JSON

from app.core.db.adapters.dto import DTOMixin
from app.graphql.addresses.services.address_service import AddressService
from app.graphql.addresses.strawberry.address_response import AddressResponse
from app.graphql.inject import inject

from commons.db.v6.crm.links.entity_type import EntityType

from app.graphql.contacts.services.contacts_service import ContactsService
from app.graphql.contacts.strawberry.contact_response import ContactResponse
from app.graphql.links.services.links_service import LinksService


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

    @strawberry.field
    @inject
    async def addresses(
        self,
        address_service: Injected[AddressService],
    ) -> list[AddressResponse]:
        """Get all addresses for this shipping carrier."""
        addresses = await address_service.list_by_source(
            AddressSourceTypeEnum.SHIPPING_CARRIER,
            self.id,
        )
        return AddressResponse.from_orm_model_list(addresses)

    @strawberry.field
    @inject
    async def billing_address(
        self,
        address_service: Injected[AddressService],
    ) -> AddressResponse | None:
        """Get the billing address for this shipping carrier."""
        addresses = await address_service.list_by_source(
            AddressSourceTypeEnum.SHIPPING_CARRIER,
            self.id,
        )
        # Find billing address (primary if multiple)
        billing = [a for a in addresses if a.address_type == AddressTypeEnum.BILLING]
        if not billing:
            return None
        # Return primary billing address if exists, otherwise first one
        primary = next((a for a in billing if a.is_primary), None)
        return AddressResponse.from_orm_model(primary or billing[0])

    @strawberry.field
    @inject
    async def contacts(
        self,
        links_service: Injected[LinksService],
        contacts_service: Injected[ContactsService],
    ) -> list[ContactResponse]:
        """Get all contacts linked to this shipping carrier."""
        # Get linked contact IDs
        links = await links_service.get_links_for_entity(
            entity_type=EntityType.SHIPPING_CARRIER,
            entity_id=self.id,
        )
        # Filter for contact links
        contact_ids = [
            link.target_entity_id
            for link in links
            if link.target_entity_type == EntityType.CONTACT
        ] + [
            link.source_entity_id
            for link in links
            if link.source_entity_type == EntityType.CONTACT
        ]
        # Fetch contacts
        contacts = []
        for contact_id in contact_ids:
            try:
                contact = await contacts_service.get_contact(contact_id)
                contacts.append(contact)
            except Exception:
                pass  # Skip if contact not found
        return ContactResponse.from_orm_model_list(contacts)

    @strawberry.field
    @inject
    async def primary_contact(
        self,
        links_service: Injected[LinksService],
        contacts_service: Injected[ContactsService],
    ) -> ContactResponse | None:
        """Get the primary contact for this shipping carrier."""
        links = await links_service.get_links_for_entity(
            entity_type=EntityType.SHIPPING_CARRIER,
            entity_id=self.id,
        )
        contact_ids = [
            link.target_entity_id
            for link in links
            if link.target_entity_type == EntityType.CONTACT
        ] + [
            link.source_entity_id
            for link in links
            if link.source_entity_type == EntityType.CONTACT
        ]
        if not contact_ids:
            return None
        # Return first contact as primary (could add is_primary flag to links later)
        try:
            contact = await contacts_service.get_contact(contact_ids[0])
            return ContactResponse.from_orm_model(contact)
        except Exception:
            return None
