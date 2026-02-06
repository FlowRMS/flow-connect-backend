import uuid

import strawberry
from aioinject import Injected

from app.graphql.di import inject
from app.graphql.geography.services.connection_territory_service import (
    ConnectionTerritoryService,
)
from app.graphql.geography.strawberry.geography_types import SubdivisionResponse


@strawberry.type
class UpdateConnectionTerritoriesResponse:
    connection_id: strawberry.ID
    subdivisions: list[SubdivisionResponse]


@strawberry.type
class ConnectionTerritoryMutations:
    @strawberry.mutation()
    @inject
    async def update_connection_territories(
        self,
        connection_id: strawberry.ID,
        subdivision_ids: list[strawberry.ID],
        service: Injected[ConnectionTerritoryService],
    ) -> UpdateConnectionTerritoriesResponse:
        conn_uuid = uuid.UUID(str(connection_id))
        sub_uuids = [uuid.UUID(str(sid)) for sid in subdivision_ids]

        territories = await service.update_territories(conn_uuid, sub_uuids)

        return UpdateConnectionTerritoriesResponse(
            connection_id=connection_id,
            subdivisions=[
                SubdivisionResponse.from_model(t.subdivision) for t in territories
            ],
        )
