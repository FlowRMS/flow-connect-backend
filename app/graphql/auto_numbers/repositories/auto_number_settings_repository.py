from collections.abc import Sequence

from commons.db.v6 import AutoNumberEntityType, AutoNumberSetting
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class AutoNumberSettingsRepository(BaseRepository[AutoNumberSetting]):
    def __init__(
        self,
        session: AsyncSession,
        context_wrapper: ContextWrapper,
    ) -> None:
        super().__init__(session, context_wrapper, AutoNumberSetting)

    async def get_by_entity_type(
        self,
        entity_type: AutoNumberEntityType,
    ) -> AutoNumberSetting | None:
        stmt = select(AutoNumberSetting).where(
            AutoNumberSetting.entity_type == entity_type
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_entity_type_for_update(
        self,
        entity_type: AutoNumberEntityType,
    ) -> AutoNumberSetting | None:
        stmt = (
            select(AutoNumberSetting)
            .where(AutoNumberSetting.entity_type == entity_type)
            .with_for_update()
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_entity_types(
        self,
        entity_types: Sequence[AutoNumberEntityType],
    ) -> list[AutoNumberSetting]:
        if not entity_types:
            return []
        stmt = select(AutoNumberSetting).where(
            AutoNumberSetting.entity_type.in_(entity_types)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def save(self, setting: AutoNumberSetting) -> AutoNumberSetting:
        self.session.add(setting)
        await self.session.flush([setting])
        return setting
