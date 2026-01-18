from commons.db.v6.core.territories.territory import Territory
from commons.db.v6.core.territories.territory_type_enum import TerritoryTypeEnum
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper


class TerritoryLookupRepository:
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__()
        self.context = context_wrapper.get()
        self.session = session

    async def find_by_zip_code(self, zip_code: str) -> list[Territory]:
        stmt = (
            select(Territory)
            .where(Territory.zip_codes.contains([zip_code]))
            .where(Territory.active.is_(True))
            .order_by(Territory.territory_type.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_state_code(self, state_code: str) -> list[Territory]:
        stmt = (
            select(Territory)
            .where(Territory.state_codes.contains([state_code.upper()]))
            .where(Territory.active.is_(True))
            .order_by(Territory.territory_type.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_county_code(self, county_code: str) -> list[Territory]:
        stmt = (
            select(Territory)
            .where(Territory.county_codes.contains([county_code]))
            .where(Territory.active.is_(True))
            .order_by(Territory.territory_type.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_city_name(self, city_name: str) -> list[Territory]:
        stmt = (
            select(Territory)
            .where(Territory.city_names.contains([city_name]))
            .where(Territory.active.is_(True))
            .order_by(Territory.territory_type.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_geographic_data(
        self,
        zip_code: str | None = None,
        city_name: str | None = None,
        county_code: str | None = None,
        state_code: str | None = None,
    ) -> Territory | None:
        if zip_code:
            stmt = (
                select(Territory)
                .where(Territory.zip_codes.contains([zip_code]))
                .where(Territory.territory_type == TerritoryTypeEnum.TERRITORY)
                .where(Territory.active.is_(True))
            )
            result = await self.session.execute(stmt)
            territory = result.scalar_one_or_none()
            if territory:
                return territory

        if city_name:
            stmt = (
                select(Territory)
                .where(Territory.city_names.contains([city_name]))
                .where(Territory.active.is_(True))
                .order_by(Territory.territory_type.desc())
            )
            result = await self.session.execute(stmt)
            territory = result.scalars().first()
            if territory:
                return territory

        if county_code:
            stmt = (
                select(Territory)
                .where(Territory.county_codes.contains([county_code]))
                .where(Territory.active.is_(True))
                .order_by(Territory.territory_type.desc())
            )
            result = await self.session.execute(stmt)
            territory = result.scalars().first()
            if territory:
                return territory

        if state_code:
            stmt = (
                select(Territory)
                .where(Territory.state_codes.contains([state_code.upper()]))
                .where(Territory.active.is_(True))
                .order_by(Territory.territory_type.desc())
            )
            result = await self.session.execute(stmt)
            territory = result.scalars().first()
            if territory:
                return territory

        return None
