import uuid

from sqlalchemy import String, and_, cast, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.graphql.connections.models.enums import ConnectionStatus
from app.graphql.organizations.models import (
    OrgStatus,
    OrgType,
    RemoteOrg,
    TenantRegistry,
)


class OrganizationSearchRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, org_id: uuid.UUID) -> RemoteOrg | None:
        stmt = (
            select(RemoteOrg)
            .options(selectinload(RemoteOrg.memberships))
            .where(
                RemoteOrg.id == org_id,
                RemoteOrg.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_domain(
        self,
        domain: str,
        org_type: OrgType,
    ) -> RemoteOrg | None:
        stmt = (
            select(RemoteOrg)
            .where(
                RemoteOrg.domain == domain,
                cast(RemoteOrg.org_type, String) == org_type.value,
                RemoteOrg.deleted_at.is_(None),
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def search(
        self,
        search_term: str,
        *,
        org_type: OrgType,
        user_org_id: uuid.UUID,
        active: bool | None = True,
        flow_connect_member: bool | None = None,
        connected: bool | None = None,
        limit: int = 20,
        exclude_org_id: uuid.UUID | None = None,
    ) -> list[tuple[RemoteOrg, bool, ConnectionStatus | None, uuid.UUID | None]]:
        from app.graphql.connections.models.remote_connection import RemoteConnection

        tenant_exists = (
            select(TenantRegistry.id)
            .where(
                and_(
                    TenantRegistry.org_id == RemoteOrg.id,
                    TenantRegistry.status == "active",
                )
            )
            .exists()
        )

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
                    != ConnectionStatus.DECLINED.value,
                )
            )
            .exists()
        )

        connection_status_subquery = (
            select(cast(RemoteConnection.status, String))
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
                    != ConnectionStatus.DECLINED.value,
                )
            )
            .correlate(RemoteOrg)
            .scalar_subquery()
        )

        connection_id_subquery = (
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
                    != ConnectionStatus.DECLINED.value,
                )
            )
            .correlate(RemoteOrg)
            .scalar_subquery()
        )

        stmt = (
            select(
                RemoteOrg,
                tenant_exists.label("flow_connect_member"),
                connection_status_subquery.label("connection_status"),
                connection_id_subquery.label("connection_id"),
            )
            .options(selectinload(RemoteOrg.memberships))
            .where(
                cast(RemoteOrg.org_type, String) == org_type.value,
                RemoteOrg.deleted_at.is_(None),
                RemoteOrg.name.ilike(f"%{search_term}%"),
            )
        )

        match active:
            case True:
                stmt = stmt.where(
                    cast(RemoteOrg.status, String) == OrgStatus.ACTIVE.value
                )
            case False:
                stmt = stmt.where(
                    cast(RemoteOrg.status, String) != OrgStatus.ACTIVE.value
                )

        match flow_connect_member:
            case True:
                stmt = stmt.where(tenant_exists)
            case False:
                stmt = stmt.where(~tenant_exists)

        match connected:
            case True:
                stmt = stmt.where(connection_exists)
            case False:
                stmt = stmt.where(~connection_exists)

        if exclude_org_id is not None:
            stmt = stmt.where(RemoteOrg.id != exclude_org_id)

        stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return [
            (
                row.RemoteOrg,
                row.flow_connect_member,
                ConnectionStatus(row.connection_status)
                if row.connection_status
                else None,
                row.connection_id,
            )
            for row in result.all()
        ]

    async def get_names_by_ids(
        self,
        org_ids: list[uuid.UUID],
    ) -> dict[uuid.UUID, str]:
        if not org_ids:
            return {}

        stmt = select(RemoteOrg.id, RemoteOrg.name).where(
            RemoteOrg.id.in_(org_ids),
            RemoteOrg.deleted_at.is_(None),
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        return {row.id: row.name for row in rows}
