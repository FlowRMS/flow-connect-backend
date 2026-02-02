from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.crm.shipping_carriers.shipping_carrier_model import CarrierType

from app.graphql.inject import inject
from app.graphql.v2.core.shipping_carriers.services.shipping_carrier_service import (
    ShippingCarrierService,
)
from app.graphql.v2.core.shipping_carriers.strawberry.shipping_carrier_response import (
    ShippingCarrierResponse,
)


@strawberry.type
class ShippingCarriersQueries:
    """GraphQL queries for ShippingCarrier entity."""

    @strawberry.field
    @inject
    async def shipping_carriers(
        self,
        service: Injected[ShippingCarrierService],
        active_only: bool = False,
    ) -> list[ShippingCarrierResponse]:
        """Get all shipping carriers.

        Args:
            active_only: If true, only return active carriers.
        """
        if active_only:
            carriers = await service.list_active()
        else:
            carriers = await service.list_all()
        return ShippingCarrierResponse.from_orm_model_list(carriers)

    @strawberry.field
    @inject
    async def shipping_carrier(
        self,
        id: UUID,
        service: Injected[ShippingCarrierService],
    ) -> ShippingCarrierResponse:
        """Get a shipping carrier by ID."""
        carrier = await service.get_by_id(id)
        return ShippingCarrierResponse.from_orm_model(carrier)

    @strawberry.field
    @inject
    async def shipping_carrier_search(
        self,
        search_term: str,
        limit: int = 20,
        service: Injected[ShippingCarrierService] = None,  # type: ignore[assignment]
    ) -> list[ShippingCarrierResponse]:
        """Search shipping carriers by name."""
        carriers = await service.search(search_term, limit)
        return ShippingCarrierResponse.from_orm_model_list(carriers)

    @strawberry.field
    @inject
    async def shipping_carriers_by_type(
        self,
        carrier_type: CarrierType,
        active_only: bool = True,
        service: Injected[ShippingCarrierService] = None,  # type: ignore[assignment]
    ) -> list[ShippingCarrierResponse]:
        """Get shipping carriers filtered by type (PARCEL or FREIGHT).

        Args:
            carrier_type: The type of carrier to filter by.
            active_only: If true, only return active carriers.
        """
        carriers = await service.list_by_type(carrier_type, active_only)
        return ShippingCarrierResponse.from_orm_model_list(carriers)
