import uuid

from commons.auth.auth_info import AuthInfo

from app.core.flow_connect_api.flow_connect_api_client import FlowConnectApiClient
from app.core.flow_connect_api.response_handler import raise_for_api_status
from app.errors.common_errors import ConflictError
from app.graphql.connections.services import ConnectionService
from app.graphql.organizations.models import OrgType, RemoteOrg
from app.graphql.organizations.repositories import OrganizationSearchRepository
from app.graphql.organizations.strawberry import CreateOrganizationInput


class OrganizationCreationService:
    def __init__(
        self,
        api_client: FlowConnectApiClient,
        org_search_repository: OrganizationSearchRepository,
        connection_service: ConnectionService,
        auth_info: AuthInfo,
    ) -> None:
        self.api_client = api_client
        self.org_search_repository = org_search_repository
        self.connection_service = connection_service
        self.auth_info = auth_info

    async def create(self, input_data: CreateOrganizationInput) -> RemoteOrg:
        if self.auth_info.auth_provider_id is None:
            raise ValueError("auth_provider_id is required for organization creation")

        user_org_id, _ = await self.connection_service.get_user_org_and_connections(
            self.auth_info.auth_provider_id,
        )

        user_org = await self.org_search_repository.get_by_id(user_org_id)
        if user_org is None:
            raise ValueError(f"User organization not found: {user_org_id}")

        target_org_type = OrgType(user_org.org_type).get_complementary_type()

        existing_org = await self.org_search_repository.get_by_domain(
            input_data.domain,
            target_org_type,
        )
        if existing_org:
            raise ConflictError(
                f"Organization with domain '{input_data.domain}' already exists"
            )

        response = await self.api_client.post(
            "/profiles/orgs",
            {
                "name": input_data.name,
                "domain": input_data.domain,
                "org_type": target_org_type.value,
                "status": "pending",
            },
        )
        raise_for_api_status(response, context="Creating organization")

        org_id = uuid.UUID(response.json()["id"])

        if input_data.contact:
            invite_response = await self.api_client.post(
                "/people/invite-to-org",
                {
                    "org_id": str(org_id),
                    "email": input_data.contact.email,
                },
            )
            raise_for_api_status(invite_response, context="Inviting contact")

        org = await self.org_search_repository.get_by_id(org_id)
        if not org:
            raise ConflictError("Failed to fetch created organization")

        return org
