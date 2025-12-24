"""Repository for shipping carrier operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.v2.core.shipping_carriers.models import ShippingCarrier


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
        """Get all active shipping carriers."""
        stmt = select(ShippingCarrier).where(ShippingCarrier.is_active == True)
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
