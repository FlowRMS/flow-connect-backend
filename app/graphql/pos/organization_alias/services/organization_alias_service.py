import uuid
from dataclasses import dataclass

from commons.auth import AuthInfo

from app.graphql.connections.models import ConnectionStatus
from app.graphql.connections.repositories.connection_repository import (
    ConnectionRepository,
)
from app.graphql.connections.repositories.user_org_repository import UserOrgRepository
from app.graphql.organizations.repositories import OrganizationSearchRepository
from app.graphql.pos.organization_alias.exceptions import (
    AliasAlreadyExistsError,
    OrganizationAliasNotFoundError,
    OrganizationNotConnectedError,
)
from app.graphql.pos.organization_alias.models import OrganizationAlias
from app.graphql.pos.organization_alias.repositories import OrganizationAliasRepository


@dataclass
class AliasGroup:
    connected_org_id: uuid.UUID
    connected_org_name: str
    aliases: list[OrganizationAlias]


class OrganizationAliasService:
    def __init__(
        self,
        repository: OrganizationAliasRepository,
        connection_repository: ConnectionRepository,
        user_org_repository: UserOrgRepository,
        org_search_repository: OrganizationSearchRepository,
        auth_info: AuthInfo,
    ) -> None:
        self.repository = repository
        self.connection_repository = connection_repository
        self.user_org_repository = user_org_repository
        self.org_search_repository = org_search_repository
        self.auth_info = auth_info

    async def _get_user_org_id(self) -> uuid.UUID:
        if self.auth_info.auth_provider_id is None:
            raise OrganizationNotConnectedError("User not authenticated")
        return await self.user_org_repository.get_user_org_id(
            self.auth_info.auth_provider_id
        )

    async def _validate_connection_accepted(
        self,
        user_org_id: uuid.UUID,
        connected_org_id: uuid.UUID,
    ) -> None:
        connection = await self.connection_repository.get_connection_by_org_id(
            user_org_id=user_org_id,
            connected_org_id=connected_org_id,
        )
        if connection is None or connection.status != ConnectionStatus.ACCEPTED.value:
            raise OrganizationNotConnectedError(
                f"Organization {connected_org_id} is not connected"
            )

    async def create_alias(
        self,
        connected_org_id: uuid.UUID,
        alias: str,
    ) -> OrganizationAlias:
        user_org_id = await self._get_user_org_id()

        await self._validate_connection_accepted(user_org_id, connected_org_id)

        if await self.repository.alias_exists(user_org_id, alias):
            raise AliasAlreadyExistsError(f"Alias '{alias}' already exists")

        organization_alias = OrganizationAlias(
            organization_id=user_org_id,
            connected_org_id=connected_org_id,
            alias=alias,
        )
        organization_alias.created_by_id = self.auth_info.flow_user_id

        return await self.repository.create(organization_alias)

    async def delete_alias(self, alias_id: uuid.UUID) -> bool:
        user_org_id = await self._get_user_org_id()
        existing = await self.repository.get_by_id(alias_id)

        if existing is None or existing.organization_id != user_org_id:
            raise OrganizationAliasNotFoundError(f"Alias {alias_id} not found")

        return await self.repository.delete(alias_id)

    async def get_all_aliases_grouped(self) -> list[AliasGroup]:
        user_org_id = await self._get_user_org_id()
        aliases = await self.repository.get_all_by_org(user_org_id)

        if not aliases:
            return []

        connected_org_ids = list({a.connected_org_id for a in aliases})
        org_names = await self.org_search_repository.get_names_by_ids(connected_org_ids)

        groups: dict[uuid.UUID, AliasGroup] = {}
        for alias in aliases:
            if alias.connected_org_id not in groups:
                groups[alias.connected_org_id] = AliasGroup(
                    connected_org_id=alias.connected_org_id,
                    connected_org_name=org_names.get(alias.connected_org_id, ""),
                    aliases=[],
                )
            groups[alias.connected_org_id].aliases.append(alias)

        return list(groups.values())
