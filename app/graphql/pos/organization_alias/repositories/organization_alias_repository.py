import uuid
from typing import Any

from sqlalchemy import String, and_, cast, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.transient_session import TenantSession
from app.graphql.connections.models import ConnectionStatus, RemoteConnection
from app.graphql.organizations.models import RemoteOrg
from app.graphql.pos.organization_alias.models import OrganizationAlias


class OrganizationAliasRepository:
    def __init__(
        self,
        session: TenantSession,
        orgs_session: AsyncSession,
    ) -> None:
        self.session = session
        self.orgs_session = orgs_session

    async def create(self, alias: OrganizationAlias) -> OrganizationAlias:
        self.session.add(alias)
        await self.session.flush([alias])
        return alias

    async def get_by_id(self, alias_id: uuid.UUID) -> OrganizationAlias | None:
        stmt = select(OrganizationAlias).where(OrganizationAlias.id == alias_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_org_and_connected_org(
        self,
        org_id: uuid.UUID,
        connected_org_id: uuid.UUID,
    ) -> OrganizationAlias | None:
        stmt = select(OrganizationAlias).where(
            OrganizationAlias.organization_id == org_id,
            OrganizationAlias.connected_org_id == connected_org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_org(self, org_id: uuid.UUID) -> list[OrganizationAlias]:
        stmt = select(OrganizationAlias).where(
            OrganizationAlias.organization_id == org_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # noinspection DuplicatedCode
    # Common SQLAlchemy exists pattern - abstracting would reduce readability for minimal gain
    async def alias_exists(self, org_id: uuid.UUID, alias: str) -> bool:
        stmt = select(func.count()).where(
            OrganizationAlias.organization_id == org_id,
            func.lower(OrganizationAlias.alias) == func.lower(alias),
        )
        result = await self.session.execute(stmt)
        count = result.scalar_one_or_none()
        return count is not None and count > 0

    async def delete(self, alias_id: uuid.UUID) -> bool:
        stmt = delete(OrganizationAlias).where(OrganizationAlias.id == alias_id)
        result: Any = await self.session.execute(stmt)
        return result.rowcount > 0

    async def get_connected_orgs_by_name(
        self,
        user_org_id: uuid.UUID,
        org_names: list[str],
    ) -> dict[str, RemoteOrg]:
        if not org_names:
            return {}

        lower_names = [name.lower() for name in org_names]

        connection_exists = (
            select(RemoteConnection.id)
            .where(
                and_(
                    or_(
                        and_(
                            RemoteConnection.requester_org_id == user_org_id,
                            RemoteConnection.target_org_id == RemoteOrg.id,
                        ),
                        and_(
                            RemoteConnection.target_org_id == user_org_id,
                            RemoteConnection.requester_org_id == RemoteOrg.id,
                        ),
                    ),
                    cast(RemoteConnection.status, String)
                    == ConnectionStatus.ACCEPTED.value,
                )
            )
            .exists()
        )

        stmt = select(RemoteOrg).where(
            func.lower(RemoteOrg.name).in_(lower_names),
            RemoteOrg.deleted_at.is_(None),
            connection_exists,
        )

        result = await self.orgs_session.execute(stmt)
        orgs = result.scalars().all()

        return {org.name.lower(): org for org in orgs}
