"""GraphQL mutations for shipping carriers."""

from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.core.addresses.address import AddressSourceTypeEnum, AddressTypeEnum
from commons.db.v6.crm.links.entity_type import EntityType

from app.graphql.addresses.services.address_service import AddressService
from app.graphql.addresses.strawberry.address_input import AddressInput
from app.graphql.addresses.strawberry.address_response import AddressResponse
from app.graphql.inject import inject
from app.graphql.links.services.links_service import LinksService
from app.graphql.v2.core.shipping_carriers.services.shipping_carrier_service import (
    ShippingCarrierService,
)
from app.graphql.v2.core.shipping_carriers.strawberry.shipping_carrier_input import (
    ShippingCarrierInput,
)
from app.graphql.v2.core.shipping_carriers.strawberry.shipping_carrier_response import (
    ShippingCarrierResponse,
)


@strawberry.input
class ShippingCarrierAddressInput:
    """Input for creating/updating a shipping carrier's address."""

    line_1: str
    city: str
    country: str
    line_2: str | None = None
    state: str | None = None
    zip_code: str | None = None
    notes: str | None = None
    is_primary: bool = True
    address_type: AddressTypeEnum = AddressTypeEnum.BILLING


@strawberry.type
class ShippingCarriersMutations:
    """GraphQL mutations for ShippingCarrier entity."""

    @strawberry.mutation
    @inject
    async def create_shipping_carrier(
        self,
        input: ShippingCarrierInput,
        service: Injected[ShippingCarrierService],
    ) -> ShippingCarrierResponse:
        """Create a new shipping carrier."""
        carrier = await service.create(input)
        return ShippingCarrierResponse.from_orm_model(carrier)

    @strawberry.mutation
    @inject
    async def update_shipping_carrier(
        self,
        id: UUID,
        input: ShippingCarrierInput,
        service: Injected[ShippingCarrierService],
    ) -> ShippingCarrierResponse:
        """Update a shipping carrier."""
        carrier = await service.update(id, input)
        return ShippingCarrierResponse.from_orm_model(carrier)

    @strawberry.mutation
    @inject
    async def delete_shipping_carrier(
        self,
        id: UUID,
        service: Injected[ShippingCarrierService],
    ) -> bool:
        """Delete a shipping carrier."""
        return await service.delete(id)

    # Address mutations for shipping carriers
    @strawberry.mutation
    @inject
    async def set_shipping_carrier_address(
        self,
        carrier_id: UUID,
        input: ShippingCarrierAddressInput,
        carrier_service: Injected[ShippingCarrierService],
        address_service: Injected[AddressService],
    ) -> AddressResponse:
        """Set or update a shipping carrier's address.

        If an address of the same type already exists, it will be updated.
        Otherwise, a new address will be created.
        """
        # Verify carrier exists
        await carrier_service.get_by_id(carrier_id)

        # Check for existing address of this type
        existing_addresses = await address_service.list_by_source(
            AddressSourceTypeEnum.SHIPPING_CARRIER,
            carrier_id,
        )
        existing = next(
            (a for a in existing_addresses if a.address_type == input.address_type),
            None,
        )

        address_input = AddressInput(
            source_id=carrier_id,
            source_type=AddressSourceTypeEnum.SHIPPING_CARRIER,
            address_type=input.address_type,
            line_1=input.line_1,
            line_2=input.line_2,
            city=input.city,
            state=input.state,
            zip_code=input.zip_code,
            country=input.country,
            notes=input.notes,
            is_primary=input.is_primary,
        )

        if existing:
            # Update existing address
            address = await address_service.update(existing.id, address_input)
        else:
            # Create new address
            address = await address_service.create(address_input)

        return AddressResponse.from_orm_model(address)

    @strawberry.mutation
    @inject
    async def delete_shipping_carrier_address(
        self,
        carrier_id: UUID,
        address_id: UUID,
        carrier_service: Injected[ShippingCarrierService],
        address_service: Injected[AddressService],
    ) -> bool:
        """Delete a shipping carrier's address."""
        # Verify carrier exists
        await carrier_service.get_by_id(carrier_id)
        # Delete the address
        return await address_service.delete(address_id)

    # Contact link mutations for shipping carriers
    @strawberry.mutation
    @inject
    async def link_contact_to_shipping_carrier(
        self,
        carrier_id: UUID,
        contact_id: UUID,
        carrier_service: Injected[ShippingCarrierService],
        links_service: Injected[LinksService],
    ) -> bool:
        """Link a contact to a shipping carrier."""
        # Verify carrier exists
        await carrier_service.get_by_id(carrier_id)
        # Create the link
        await links_service.create_link(
            source_type=EntityType.SHIPPING_CARRIER,
            source_id=carrier_id,
            target_type=EntityType.CONTACT,
            target_id=contact_id,
        )
        return True

    @strawberry.mutation
    @inject
    async def unlink_contact_from_shipping_carrier(
        self,
        carrier_id: UUID,
        contact_id: UUID,
        carrier_service: Injected[ShippingCarrierService],
        links_service: Injected[LinksService],
    ) -> bool:
        """Unlink a contact from a shipping carrier."""
        # Verify carrier exists
        await carrier_service.get_by_id(carrier_id)
        # Delete the link
        return await links_service.delete_link_by_entities(
            source_type=EntityType.SHIPPING_CARRIER,
            source_id=carrier_id,
            target_type=EntityType.CONTACT,
            target_id=contact_id,
        )
