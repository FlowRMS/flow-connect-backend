from uuid import UUID

from commons.db.v6.crm import (
    SidebarConfiguration,
    SidebarConfigurationGroup,
    SidebarConfigurationItem,
)
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.context_wrapper import ContextWrapper


class SidebarConfigurationRepository:
    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__()
        self.session = session
        self.context = context_wrapper.get()

    async def get_by_id(
        self,
        config_id: UUID,
        *,
        load_relations: bool = True,
    ) -> SidebarConfiguration | None:
        stmt = select(SidebarConfiguration).where(SidebarConfiguration.id == config_id)
        if load_relations:
            stmt = stmt.options(
                selectinload(SidebarConfiguration.groups),
                selectinload(SidebarConfiguration.items),
            )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_admin_configurations(self) -> list[SidebarConfiguration]:
        stmt = (
            select(SidebarConfiguration)
            .where(SidebarConfiguration.owner_type == "admin")
            .options(
                selectinload(SidebarConfiguration.groups),
                selectinload(SidebarConfiguration.items),
            )
            .order_by(SidebarConfiguration.name)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def get_user_configurations(
        self, user_id: UUID
    ) -> list[SidebarConfiguration]:
        stmt = (
            select(SidebarConfiguration)
            .where(
                SidebarConfiguration.owner_type == "user",
                SidebarConfiguration.owner_id == user_id,
            )
            .options(
                selectinload(SidebarConfiguration.groups),
                selectinload(SidebarConfiguration.items),
            )
            .order_by(SidebarConfiguration.name)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def get_user_default_configuration(
        self, user_id: UUID
    ) -> SidebarConfiguration | None:
        stmt = (
            select(SidebarConfiguration)
            .where(
                SidebarConfiguration.owner_type == "user",
                SidebarConfiguration.owner_id == user_id,
                SidebarConfiguration.is_default == True,  # noqa: E712
            )
            .options(
                selectinload(SidebarConfiguration.groups),
                selectinload(SidebarConfiguration.items),
            )
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def create(
        self,
        config: SidebarConfiguration,
        groups: list[SidebarConfigurationGroup],
        items: list[SidebarConfigurationItem],
    ) -> SidebarConfiguration:
        self.session.add(config)
        await self.session.flush([config])

        for group in groups:
            group.configuration_id = config.id
            self.session.add(group)

        for item in items:
            item.configuration_id = config.id
            self.session.add(item)

        await self.session.flush()
        return await self.get_by_id(config.id)  # type: ignore

    async def update(
        self,
        config: SidebarConfiguration,
        groups: list[SidebarConfigurationGroup],
        items: list[SidebarConfigurationItem],
    ) -> SidebarConfiguration:
        # Delete existing groups and items
        _ = await self.session.execute(
            delete(SidebarConfigurationGroup).where(
                SidebarConfigurationGroup.configuration_id == config.id
            )
        )
        _ = await self.session.execute(
            delete(SidebarConfigurationItem).where(
                SidebarConfigurationItem.configuration_id == config.id
            )
        )

        # Add new groups and items
        for group in groups:
            group.configuration_id = config.id
            self.session.add(group)

        for item in items:
            item.configuration_id = config.id
            self.session.add(item)

        await self.session.flush()
        return await self.get_by_id(config.id)  # type: ignore

    async def delete(self, config_id: UUID) -> bool:
        stmt = delete(SidebarConfiguration).where(SidebarConfiguration.id == config_id)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0  # type: ignore[union-attr]

    async def clear_user_default(self, user_id: UUID) -> None:
        stmt = select(SidebarConfiguration).where(
            SidebarConfiguration.owner_type == "user",
            SidebarConfiguration.owner_id == user_id,
            SidebarConfiguration.is_default == True,  # noqa: E712
        )
        result = await self.session.execute(stmt)
        configs = result.scalars().all()
        for config in configs:
            config.is_default = False
        await self.session.flush()
