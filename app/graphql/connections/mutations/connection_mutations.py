import uuid

import strawberry
from aioinject import Injected

from app.graphql.connections.services.connection_request_service import (
    ConnectionRequestService,
)
from app.graphql.di import inject


@strawberry.type
class ConnectionMutations:
    @strawberry.mutation()
    @inject
    async def create_connection(
        self,
        target_org_id: strawberry.ID,
        service: Injected[ConnectionRequestService],
        draft: bool = False,
    ) -> bool:
        return await service.create_connection_request(
            uuid.UUID(str(target_org_id)),
            draft=draft,
        )

    @strawberry.mutation()
    @inject
    async def invite_connection(
        self,
        target_org_id: strawberry.ID,
        service: Injected[ConnectionRequestService],
    ) -> bool:
        return await service.invite_connection(uuid.UUID(str(target_org_id)))
