import uuid

from sqlalchemy import String, and_, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.connections.models import ConnectionStatus, RemoteConnection


class ConnectionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, connection_id: uuid.UUID) -> RemoteConnection | None:
        stmt = select(RemoteConnection).where(RemoteConnection.id == connection_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_connection_by_org_id(
        self,
        user_org_id: uuid.UUID,
        connected_org_id: uuid.UUID,
    ) -> RemoteConnection | None:
        stmt = select(RemoteConnection).where(
            or_(
                and_(
                    RemoteConnection.requester_org_id == user_org_id,
                    RemoteConnection.target_org_id == connected_org_id,
                ),
                and_(
                    RemoteConnection.target_org_id == user_org_id,
                    RemoteConnection.requester_org_id == connected_org_id,
                ),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_connected_org_ids(
        self,
        user_org_id: uuid.UUID,
        candidate_org_ids: list[uuid.UUID],
    ) -> set[uuid.UUID]:
        if not candidate_org_ids:
            return set()

        stmt = select(RemoteConnection).where(
            and_(
                or_(
                    and_(
                        RemoteConnection.requester_org_id == user_org_id,
                        RemoteConnection.target_org_id.in_(candidate_org_ids),
                    ),
                    and_(
                        RemoteConnection.target_org_id == user_org_id,
                        RemoteConnection.requester_org_id.in_(candidate_org_ids),
                    ),
                ),
                cast(RemoteConnection.status, String)
                != ConnectionStatus.DECLINED.value,
            )
        )

        result = await self.session.execute(stmt)
        connections = result.scalars().all()

        connected_ids: set[uuid.UUID] = set()
        for conn in connections:
            if conn.requester_org_id == user_org_id:
                connected_ids.add(conn.target_org_id)
            else:
                connected_ids.add(conn.requester_org_id)

        return connected_ids

    async def count_by_status(self, org_id: uuid.UUID, status: ConnectionStatus) -> int:
        stmt = select(func.count()).where(
            or_(
                RemoteConnection.requester_org_id == org_id,
                RemoteConnection.target_org_id == org_id,
            ),
            cast(RemoteConnection.status, String) == status.value,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
