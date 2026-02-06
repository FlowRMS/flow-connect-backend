import uuid

from commons.auth.auth_info import AuthInfo

from app.graphql.connections.models.enums import ConnectionStatus
from app.graphql.connections.services import ConnectionService
from app.graphql.geography.models import Subdivision
from app.graphql.geography.repositories.connection_territory_repository import (
    ConnectionTerritoryRepository,
)
from app.graphql.organizations.models import OrgType, RemoteOrg
from app.graphql.organizations.repositories import OrganizationSearchRepository
from app.graphql.organizations.repositories.pos_contact_repository import (
    OrgPosContacts,
    PosContactRepository,
)
from app.graphql.organizations.services.organization_search_result import (
    OrganizationSearchResult,
)
from app.graphql.pos.agreement.models.agreement import Agreement
from app.graphql.pos.agreement.services.agreement_service import AgreementService


class OrganizationSearchService:
    def __init__(
        self,
        org_search_repository: OrganizationSearchRepository,
        pos_contact_repository: PosContactRepository,
        connection_service: ConnectionService,
        agreement_service: AgreementService,
        territory_repository: ConnectionTerritoryRepository,
        auth_info: AuthInfo,
    ) -> None:
        self.org_search_repository = org_search_repository
        self.pos_contact_repository = pos_contact_repository
        self.connection_service = connection_service
        self.agreement_service = agreement_service
        self.territory_repository = territory_repository
        self.auth_info = auth_info

    async def search_for_connections(
        self,
        search_term: str,
        *,
        active: bool | None = True,
        flow_connect_member: bool | None = None,
        connected: bool | None = None,
        limit: int = 20,
        rep_firms: bool = False,
    ) -> list[OrganizationSearchResult]:
        if self.auth_info.auth_provider_id is None:
            raise ValueError("auth_provider_id is required for connection search")

        workos_user_id = self.auth_info.auth_provider_id
        user_org_id, _ = await self.connection_service.get_user_org_and_connections(
            workos_user_id,
        )

        user_org = await self.org_search_repository.get_by_id(user_org_id)
        if user_org is None:
            raise ValueError(f"User organization not found: {user_org_id}")

        user_org_type = OrgType(user_org.org_type)

        if rep_firms:
            if user_org_type != OrgType.MANUFACTURER:
                raise ValueError("Only manufacturers can search for rep firms")
            target_org_type = OrgType.REP_FIRM
        else:
            target_org_type = user_org_type.get_complementary_type()

        return await self.search(
            target_org_type,
            search_term,
            active=active,
            flow_connect_member=flow_connect_member,
            connected=connected,
            limit=limit,
            rep_firms=rep_firms,
        )

    async def search(
        self,
        org_type: OrgType,
        search_term: str,
        *,
        active: bool | None = True,
        flow_connect_member: bool | None = None,
        connected: bool | None = None,
        limit: int = 20,
        rep_firms: bool = False,
    ) -> list[OrganizationSearchResult]:
        if self.auth_info.auth_provider_id is None:
            raise ValueError("auth_provider_id is required for organization search")

        workos_user_id = self.auth_info.auth_provider_id

        user_org_id, _ = await self.connection_service.get_user_org_and_connections(
            workos_user_id,
        )

        org_results = await self.org_search_repository.search(
            search_term,
            org_type=org_type,
            user_org_id=user_org_id,
            active=active,
            flow_connect_member=flow_connect_member,
            connected=connected,
            limit=limit,
            exclude_org_id=user_org_id,
        )

        if not org_results:
            return []

        org_ids = [org.id for org, _, _, _ in org_results]
        pos_contacts_map = await self.pos_contact_repository.get_pos_contacts_for_orgs(
            org_ids
        )

        accepted_org_ids = [
            org.id
            for org, _, conn_status, _ in org_results
            if conn_status == ConnectionStatus.ACCEPTED
        ]
        agreements_map: dict[str, tuple[Agreement, str]] = {}
        for org_id in accepted_org_ids:
            agreement = await self.agreement_service.get_agreement(org_id)
            if agreement:
                presigned_url = await self.agreement_service.get_presigned_url(
                    agreement
                )
                agreements_map[str(org_id)] = (agreement, presigned_url)

        # Fetch subdivisions for connected rep firms
        subdivisions_map = await self._get_subdivisions_map(org_results, rep_firms)

        return [
            OrganizationSearchResult(
                org=org,
                flow_connect_member=is_member,
                pos_contacts=pos_contacts_map.get(
                    org.id,
                    OrgPosContacts(contacts=[], total_count=0),
                ),
                connection_status=conn_status,
                connection_id=conn_id,
                agreement_data=agreements_map.get(str(org.id)),
                subdivisions=subdivisions_map.get(conn_id) if conn_id else None,
            )
            for org, is_member, conn_status, conn_id in org_results
        ]

    async def _get_subdivisions_map(
        self,
        org_results: list[
            tuple[RemoteOrg, bool, ConnectionStatus | None, uuid.UUID | None]
        ],
        rep_firms: bool,
    ) -> dict[uuid.UUID, list[Subdivision]]:
        if not rep_firms:
            return {}

        connected_ids = [
            conn_id
            for _, _, conn_status, conn_id in org_results
            if conn_status == ConnectionStatus.ACCEPTED and conn_id
        ]

        if not connected_ids:
            return {}

        subdivisions_map: dict[uuid.UUID, list[Subdivision]] = {}
        for conn_id in connected_ids:
            subdivisions = (
                await self.territory_repository.get_subdivisions_by_connection_id(
                    conn_id
                )
            )
            subdivisions_map[conn_id] = subdivisions

        return subdivisions_map
