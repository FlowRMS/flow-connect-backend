import uuid

from app.graphql.connections.repositories.connection_repository import (
    ConnectionRepository,
)
from app.graphql.connections.repositories.user_org_repository import UserOrgRepository


class ConnectionService:
    def __init__(
        self,
        user_org_repository: UserOrgRepository,
        connection_repository: ConnectionRepository,
    ) -> None:
        self.user_org_repository = user_org_repository
        self.connection_repository = connection_repository

    async def get_user_org_and_connections(
        self,
        workos_user_id: str,
        candidate_org_ids: list[uuid.UUID] | None = None,
    ) -> tuple[uuid.UUID, set[uuid.UUID]]:
        user_org_id = await self.user_org_repository.get_user_org_id(workos_user_id)

        connected_org_ids = await self.connection_repository.get_connected_org_ids(
            user_org_id, candidate_org_ids or []
        )

        return user_org_id, connected_org_ids
