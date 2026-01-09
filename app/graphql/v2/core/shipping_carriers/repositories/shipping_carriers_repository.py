"""Repository for shipping carrier operations."""

from commons.db.v6 import ShippingCarrier
from commons.db.v6.crm.shipping_carriers.shipping_carrier_model import CarrierType
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class ShippingCarriersRepository(BaseRepository[ShippingCarrier]):
    """Repository for ShippingCarrier entity."""

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            ShippingCarrier,
        )

    async def list_active(self) -> list[ShippingCarrier]:
        stmt = select(ShippingCarrier).where(ShippingCarrier.is_active.is_(True))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_type(
        self, carrier_type_str: str, active_only: bool = True
    ) -> list[ShippingCarrier]:
        """List carriers filtered by type (PARCEL or FREIGHT)."""
        # Convert string to CarrierType enum
        carrier_type = (
            CarrierType.PARCEL if carrier_type_str == "PARCEL" else CarrierType.FREIGHT
        )

        stmt = select(ShippingCarrier).where(
            ShippingCarrier.carrier_type == carrier_type
        )
        if active_only:
            stmt = stmt.where(ShippingCarrier.is_active.is_(True))

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_name(
        self, search_term: str, limit: int = 20
    ) -> list[ShippingCarrier]:
        """Search carriers by name."""
        stmt = (
            select(ShippingCarrier)
            .where(ShippingCarrier.name.ilike(f"%{search_term}%"))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
