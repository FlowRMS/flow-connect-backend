import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.errors.common_errors import ConflictError, RemoteApiError
from app.graphql.organizations.services.organization_creation_service import (
    OrganizationCreationService,
)
from app.graphql.organizations.strawberry import CreateOrganizationInput, PosContactInput


class TestOrganizationCreationService:
    @pytest.fixture
    def mock_api_client(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_org_search_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def user_org_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.fixture
    def mock_connection_service(self, user_org_id: uuid.UUID) -> AsyncMock:
        mock = AsyncMock()
        mock.get_user_org_and_connections.return_value = (user_org_id, [])
        return mock

    @pytest.fixture
    def mock_auth_info(self) -> MagicMock:
        auth_info = MagicMock()
        auth_info.auth_provider_id = "workos-user-123"
        return auth_info

    @pytest.fixture
    def mock_user_org(self) -> MagicMock:
        """Default user org is a distributor (creates manufacturers)."""
        mock = MagicMock()
        mock.org_type = "distributor"
        return mock

    @pytest.fixture
    def service(
        self,
        mock_api_client: AsyncMock,
        mock_org_search_repo: AsyncMock,
        mock_connection_service: AsyncMock,
        mock_auth_info: MagicMock,
        mock_user_org: MagicMock,
    ) -> OrganizationCreationService:
        return OrganizationCreationService(
            api_client=mock_api_client,
            org_search_repository=mock_org_search_repo,
            connection_service=mock_connection_service,
            auth_info=mock_auth_info,
        )

    @pytest.mark.asyncio
    async def test_create_success_when_domain_not_exists(
        self,
        service: OrganizationCreationService,
        mock_api_client: AsyncMock,
        mock_org_search_repo: AsyncMock,
        mock_user_org: MagicMock,
    ) -> None:
        """Creates org via API when domain doesn't exist."""
        org_id = uuid.uuid4()
        mock_org_search_repo.get_by_domain.return_value = None

        mock_create_response = MagicMock()
        mock_create_response.status_code = 201
        mock_create_response.json.return_value = {"id": str(org_id)}
        mock_api_client.post.return_value = mock_create_response

        mock_created_org = MagicMock()
        mock_created_org.id = org_id
        mock_org_search_repo.get_by_id.side_effect = [mock_user_org, mock_created_org]

        input_data = CreateOrganizationInput(name="Test Manufacturer", domain="test.com")
        result = await service.create(input_data)

        assert result.id == org_id
        mock_api_client.post.assert_called_once_with(
            "/profiles/orgs",
            {
                "name": "Test Manufacturer",
                "domain": "test.com",
                "org_type": "manufacturer",
                "status": "pending",
            },
        )

    @pytest.mark.asyncio
    async def test_create_with_contact_creates_invitation(
        self,
        service: OrganizationCreationService,
        mock_api_client: AsyncMock,
        mock_org_search_repo: AsyncMock,
        mock_user_org: MagicMock,
    ) -> None:
        """Creates pending invitation when contact is provided."""
        org_id = uuid.uuid4()
        mock_org_search_repo.get_by_domain.return_value = None

        mock_create_response = MagicMock()
        mock_create_response.status_code = 201
        mock_create_response.json.return_value = {"id": str(org_id)}

        mock_invite_response = MagicMock()
        mock_invite_response.status_code = 201

        mock_api_client.post.side_effect = [mock_create_response, mock_invite_response]

        mock_created_org = MagicMock()
        mock_created_org.id = org_id
        mock_org_search_repo.get_by_id.side_effect = [mock_user_org, mock_created_org]

        input_data = CreateOrganizationInput(
            name="Test Manufacturer",
            domain="test.com",
            contact=PosContactInput(email="admin@test.com"),
        )
        await service.create(input_data)

        assert mock_api_client.post.call_count == 2
        mock_api_client.post.assert_any_call(
            "/people/invite-to-org",
            {
                "org_id": str(org_id),
                "email": "admin@test.com",
            },
        )

    @pytest.mark.asyncio
    async def test_create_raises_conflict_when_domain_exists(
        self,
        service: OrganizationCreationService,
        mock_org_search_repo: AsyncMock,
        mock_user_org: MagicMock,
    ) -> None:
        """Raises ConflictError if organization with domain already exists."""
        mock_org_search_repo.get_by_id.return_value = mock_user_org

        existing_org = MagicMock()
        existing_org.id = uuid.uuid4()
        mock_org_search_repo.get_by_domain.return_value = existing_org

        input_data = CreateOrganizationInput(name="Test Manufacturer", domain="existing.com")

        with pytest.raises(ConflictError):
            await service.create(input_data)

    @pytest.mark.asyncio
    async def test_create_raises_error_on_api_failure(
        self,
        service: OrganizationCreationService,
        mock_api_client: AsyncMock,
        mock_org_search_repo: AsyncMock,
        mock_user_org: MagicMock,
    ) -> None:
        """Raises RemoteApiError when org creation API fails."""
        mock_org_search_repo.get_by_id.return_value = mock_user_org
        mock_org_search_repo.get_by_domain.return_value = None

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_api_client.post.return_value = mock_response

        input_data = CreateOrganizationInput(name="Test Manufacturer", domain="test.com")

        with pytest.raises(RemoteApiError):
            await service.create(input_data)

    @pytest.mark.asyncio
    async def test_create_raises_error_on_invitation_failure(
        self,
        service: OrganizationCreationService,
        mock_api_client: AsyncMock,
        mock_org_search_repo: AsyncMock,
        mock_user_org: MagicMock,
    ) -> None:
        """Raises RemoteApiError when invitation API fails."""
        org_id = uuid.uuid4()
        mock_org_search_repo.get_by_id.return_value = mock_user_org
        mock_org_search_repo.get_by_domain.return_value = None

        mock_create_response = MagicMock()
        mock_create_response.status_code = 201
        mock_create_response.json.return_value = {"id": str(org_id)}

        mock_invite_response = MagicMock()
        mock_invite_response.status_code = 500

        mock_api_client.post.side_effect = [mock_create_response, mock_invite_response]

        input_data = CreateOrganizationInput(
            name="Test Manufacturer",
            domain="test.com",
            contact=PosContactInput(email="admin@test.com"),
        )

        with pytest.raises(RemoteApiError):
            await service.create(input_data)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("user_org_type", "expected_created_type"),
        [
            ("distributor", "manufacturer"),
            ("manufacturer", "distributor"),
        ],
    )
    async def test_create_uses_complementary_org_type(
        self,
        service: OrganizationCreationService,
        mock_api_client: AsyncMock,
        mock_org_search_repo: AsyncMock,
        mock_connection_service: AsyncMock,
        user_org_type: str,
        expected_created_type: str,
    ) -> None:
        """Creates complementary org type based on user's org type."""
        user_org_id = uuid.uuid4()
        created_org_id = uuid.uuid4()

        mock_connection_service.get_user_org_and_connections.return_value = (
            user_org_id,
            [],
        )

        mock_user_org = MagicMock()
        mock_user_org.org_type = user_org_type

        mock_org_search_repo.get_by_domain.return_value = None
        mock_org_search_repo.get_by_id.side_effect = [
            mock_user_org,
            MagicMock(id=created_org_id),
        ]

        mock_create_response = MagicMock()
        mock_create_response.status_code = 201
        mock_create_response.json.return_value = {"id": str(created_org_id)}
        mock_api_client.post.return_value = mock_create_response

        input_data = CreateOrganizationInput(name="Test Org", domain="test.com")
        await service.create(input_data)

        mock_api_client.post.assert_called_once_with(
            "/profiles/orgs",
            {
                "name": "Test Org",
                "domain": "test.com",
                "org_type": expected_created_type,
                "status": "pending",
            },
        )
