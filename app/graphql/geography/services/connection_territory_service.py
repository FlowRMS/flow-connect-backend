import uuid

from commons.auth.auth_info import AuthInfo

from app.graphql.connections.repositories.connection_repository import (
    ConnectionRepository,
)
from app.graphql.connections.services import ConnectionService
from app.graphql.geography.models import ConnectionTerritory
from app.graphql.geography.repositories.connection_territory_repository import (
    ConnectionTerritoryRepository,
)
from app.graphql.geography.repositories.subdivision_repository import (
    SubdivisionRepository,
)
from app.graphql.organizations.models import OrgType
from app.graphql.organizations.repositories import OrganizationSearchRepository


class ConnectionTerritoryService:
    def __init__(
        self,
        territory_repository: ConnectionTerritoryRepository,
        subdivision_repository: SubdivisionRepository,
        connection_repository: ConnectionRepository,
        org_search_repository: OrganizationSearchRepository,
        connection_service: ConnectionService,
        auth_info: AuthInfo,
    ) -> None:
        self.territory_repository = territory_repository
        self.subdivision_repository = subdivision_repository
        self.connection_repository = connection_repository
        self.org_search_repository = org_search_repository
        self.connection_service = connection_service
        self.auth_info = auth_info

    async def update_territories(
        self,
        connection_id: uuid.UUID,
        subdivision_ids: list[uuid.UUID],
    ) -> list[ConnectionTerritory]:
        if self.auth_info.auth_provider_id is None:
            raise ValueError("auth_provider_id is required")

        workos_user_id = self.auth_info.auth_provider_id
        user_org_id, _ = await self.connection_service.get_user_org_and_connections(
            workos_user_id,
        )

        user_org = await self.org_search_repository.get_by_id(user_org_id)
        if user_org is None:
            raise ValueError(f"User organization not found: {user_org_id}")

        user_org_type = OrgType(user_org.org_type)
        if user_org_type != OrgType.MANUFACTURER:
            raise ValueError("Only manufacturers can update connection territories")

        connection = await self.connection_repository.get_by_id(connection_id)
        if connection is None:
            raise ValueError(f"Connection not found: {connection_id}")

        if (
            connection.requester_org_id != user_org_id
            and connection.target_org_id != user_org_id
        ):
            raise ValueError(
                f"User is not authorized to update territories for connection: "
                f"{connection_id}"
            )

        if subdivision_ids:
            subdivisions = await self.subdivision_repository.get_by_ids(subdivision_ids)
            if len(subdivisions) != len(subdivision_ids):
                found_ids = {s.id for s in subdivisions}
                missing_ids = set(subdivision_ids) - found_ids
                raise ValueError(f"Invalid subdivision IDs: {missing_ids}")

        return await self.territory_repository.set_territories(
            connection_id, subdivision_ids
        )
