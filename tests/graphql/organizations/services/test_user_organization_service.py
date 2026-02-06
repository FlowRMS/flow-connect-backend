import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.connections.exceptions import (
    UserNotFoundError,
    UserOrganizationRequiredError,
)
from app.graphql.organizations.services.user_organization_service import (
    UserOrganizationService,
)


class TestGetUserOrganization:
    @pytest.fixture
    def organization_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.fixture
    def mock_user_org_repository(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def mock_org_search_repository(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def mock_auth_info(self) -> MagicMock:
        auth_info = MagicMock()
        auth_info.auth_provider_id = "workos_user_123"
        return auth_info

    @pytest.fixture
    def service(
        self,
        mock_user_org_repository: MagicMock,
        mock_org_search_repository: MagicMock,
        mock_auth_info: MagicMock,
    ) -> UserOrganizationService:
        return UserOrganizationService(
            user_org_repository=mock_user_org_repository,
            org_search_repository=mock_org_search_repository,
            auth_info=mock_auth_info,
        )

    @pytest.mark.asyncio
    async def test_get_user_organization_returns_org(
        self,
        service: UserOrganizationService,
        mock_user_org_repository: MagicMock,
        mock_org_search_repository: MagicMock,
        organization_id: uuid.UUID,
    ) -> None:
        mock_org = MagicMock()
        mock_org.id = organization_id
        mock_org.name = "Test Org"
        mock_org.org_type = "manufacturer"

        mock_user_org_repository.get_user_org_id = AsyncMock(
            return_value=organization_id
        )
        mock_org_search_repository.get_by_id = AsyncMock(return_value=mock_org)

        result = await service.get_user_organization()

        assert result == mock_org
        mock_user_org_repository.get_user_org_id.assert_called_once_with(
            "workos_user_123"
        )
        mock_org_search_repository.get_by_id.assert_called_once_with(organization_id)

    @pytest.mark.asyncio
    async def test_get_user_organization_user_not_found(
        self,
        service: UserOrganizationService,
        mock_user_org_repository: MagicMock,
    ) -> None:
        mock_user_org_repository.get_user_org_id = AsyncMock(
            side_effect=UserNotFoundError("workos_user_123")
        )

        with pytest.raises(UserNotFoundError):
            await service.get_user_organization()

    @pytest.mark.asyncio
    async def test_get_user_organization_no_primary_org(
        self,
        service: UserOrganizationService,
        mock_user_org_repository: MagicMock,
    ) -> None:
        mock_user_org_repository.get_user_org_id = AsyncMock(
            side_effect=UserOrganizationRequiredError("workos_user_123")
        )

        with pytest.raises(UserOrganizationRequiredError):
            await service.get_user_organization()

    @pytest.mark.asyncio
    async def test_get_user_organization_org_not_found(
        self,
        service: UserOrganizationService,
        mock_user_org_repository: MagicMock,
        mock_org_search_repository: MagicMock,
        organization_id: uuid.UUID,
    ) -> None:
        mock_user_org_repository.get_user_org_id = AsyncMock(
            return_value=organization_id
        )
        mock_org_search_repository.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="User organization not found"):
            await service.get_user_organization()

    @pytest.mark.asyncio
    async def test_get_user_organization_no_auth_provider_id(
        self,
        mock_user_org_repository: MagicMock,
        mock_org_search_repository: MagicMock,
    ) -> None:
        auth_info = MagicMock()
        auth_info.auth_provider_id = None

        service = UserOrganizationService(
            user_org_repository=mock_user_org_repository,
            org_search_repository=mock_org_search_repository,
            auth_info=auth_info,
        )

        with pytest.raises(ValueError, match="Auth provider ID is required"):
            await service.get_user_organization()
