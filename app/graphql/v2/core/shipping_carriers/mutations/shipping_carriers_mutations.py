"""GraphQL mutations for shipping carriers."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.shipping_carriers.services.shipping_carrier_service import (
    ShippingCarrierService,
)
from app.graphql.v2.core.shipping_carriers.strawberry.shipping_carrier_input import (
    ShippingCarrierInput,
)
from app.graphql.v2.core.shipping_carriers.strawberry.shipping_carrier_response import (
    ShippingCarrierResponse,
)


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
