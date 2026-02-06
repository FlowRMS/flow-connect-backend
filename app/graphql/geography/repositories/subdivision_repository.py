import uuid

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.db.transient_session import TenantSession
from app.graphql.geography.models import Subdivision


class SubdivisionRepository:
    def __init__(self, session: TenantSession) -> None:
        self.session = session

    async def get_by_id(self, subdivision_id: uuid.UUID) -> Subdivision | None:
        stmt = select(Subdivision).where(Subdivision.id == subdivision_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(self, subdivision_ids: list[uuid.UUID]) -> list[Subdivision]:
        if not subdivision_ids:
            return []
        stmt = select(Subdivision).where(Subdivision.id.in_(subdivision_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_by_country_id(
        self,
        country_id: uuid.UUID,
    ) -> list[Subdivision]:
        stmt = (
            select(Subdivision)
            .where(Subdivision.country_id == country_id)
            .order_by(Subdivision.name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all(self) -> list[Subdivision]:
        stmt = (
            select(Subdivision)
            .options(joinedload(Subdivision.country))
            .order_by(Subdivision.iso_code)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
