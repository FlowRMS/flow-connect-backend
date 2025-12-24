"""Service layer for shipping carrier operations."""

from uuid import UUID

from commons.auth import AuthInfo

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.shipping_carriers.models import ShippingCarrier
from app.graphql.v2.core.shipping_carriers.repositories import ShippingCarriersRepository
from app.graphql.v2.core.shipping_carriers.strawberry.shipping_carrier_input import (
    ShippingCarrierInput,
)


class ShippingCarrierService:
    """Service for shipping carrier operations."""

    def __init__(
        self,
        repository: ShippingCarriersRepository,
        auth_info: AuthInfo,
    ) -> None:
        self.repository = repository
        self.auth_info = auth_info

    async def get_by_id(self, carrier_id: UUID) -> ShippingCarrier:
        """Get a shipping carrier by ID."""
        carrier = await self.repository.get_by_id(carrier_id)
        if not carrier:
            raise NotFoundError(f"Shipping carrier with id {carrier_id} not found")
        return carrier

    async def list_all(self) -> list[ShippingCarrier]:
        """Get all shipping carriers."""
        return await self.repository.list_all()

    async def list_active(self) -> list[ShippingCarrier]:
        """Get all active shipping carriers."""
        return await self.repository.list_active()

    async def create(self, input: ShippingCarrierInput) -> ShippingCarrier:
        """Create a new shipping carrier."""
        return await self.repository.create(input.to_orm_model())

    async def update(
        self, carrier_id: UUID, input: ShippingCarrierInput
    ) -> ShippingCarrier:
        """Update a shipping carrier."""
        carrier = input.to_orm_model()
        carrier.id = carrier_id
        return await self.repository.update(carrier)

    async def delete(self, carrier_id: UUID) -> bool:
        """Delete a shipping carrier."""
        if not await self.repository.exists(carrier_id):
            raise NotFoundError(f"Shipping carrier with id {carrier_id} not found")
        return await self.repository.delete(carrier_id)

    async def search(self, search_term: str, limit: int = 20) -> list[ShippingCarrier]:
        """Search carriers by name."""
        return await self.repository.search_by_name(search_term, limit)
