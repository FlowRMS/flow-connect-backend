import uuid
from typing import Any

from sqlalchemy import delete, func, select

from app.core.db.transient_session import TenantSession
from app.graphql.pos.validations.models import PrefixPattern


class PrefixPatternRepository:
    def __init__(self, session: TenantSession) -> None:
        self.session = session

    async def create(self, pattern: PrefixPattern) -> PrefixPattern:
        self.session.add(pattern)
        await self.session.flush([pattern])
        return pattern

    async def get_by_id(self, pattern_id: uuid.UUID) -> PrefixPattern | None:
        stmt = select(PrefixPattern).where(PrefixPattern.id == pattern_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_org(self, org_id: uuid.UUID) -> list[PrefixPattern]:
        stmt = select(PrefixPattern).where(PrefixPattern.organization_id == org_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, pattern_id: uuid.UUID) -> bool:
        stmt = delete(PrefixPattern).where(PrefixPattern.id == pattern_id)
        result: Any = await self.session.execute(stmt)
        return result.rowcount > 0

    # noinspection DuplicatedCode
    # Common SQLAlchemy exists pattern - abstracting would reduce readability for minimal gain
    async def exists_by_org_and_name(self, org_id: uuid.UUID, name: str) -> bool:
        stmt = select(func.count()).where(
            PrefixPattern.organization_id == org_id,
            func.lower(PrefixPattern.name) == func.lower(name),
        )
        result = await self.session.execute(stmt)
        count = result.scalar_one_or_none()
        return count is not None and count > 0
