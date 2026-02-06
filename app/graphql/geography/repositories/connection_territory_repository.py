import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload

from app.core.db.transient_session import TenantSession
from app.graphql.geography.models import ConnectionTerritory, Subdivision


class ConnectionTerritoryRepository:
    def __init__(self, session: TenantSession) -> None:
        self.session = session

    async def get_by_connection_id(
        self,
        connection_id: uuid.UUID,
    ) -> list[ConnectionTerritory]:
        stmt = (
            select(ConnectionTerritory)
            .options(joinedload(ConnectionTerritory.subdivision))
            .where(ConnectionTerritory.connection_id == connection_id)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def get_subdivisions_by_connection_id(
        self,
        connection_id: uuid.UUID,
    ) -> list[Subdivision]:
        territories = await self.get_by_connection_id(connection_id)
        return [t.subdivision for t in territories]

    async def set_territories(
        self,
        connection_id: uuid.UUID,
        subdivision_ids: list[uuid.UUID],
    ) -> list[ConnectionTerritory]:
        # Delete existing territories
        delete_stmt = delete(ConnectionTerritory).where(
            ConnectionTerritory.connection_id == connection_id
        )
        await self.session.execute(delete_stmt)

        # Create new territories
        territories: list[ConnectionTerritory] = []
        for subdivision_id in subdivision_ids:
            territory = ConnectionTerritory(
                connection_id=connection_id,
                subdivision_id=subdivision_id,
            )
            self.session.add(territory)
            territories.append(territory)

        if territories:
            await self.session.flush(territories)

        return territories
