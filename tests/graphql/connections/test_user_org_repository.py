import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.connections.exceptions import (
    UserNotFoundError,
    UserOrganizationRequiredError,
)
from app.graphql.connections.repositories.user_org_repository import UserOrgRepository


class TestUserOrgRepository:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def repository(self, mock_session: AsyncMock) -> UserOrgRepository:
        return UserOrgRepository(session=mock_session)

    @pytest.mark.asyncio
    async def test_get_user_org_id_returns_org_id_for_valid_user(
        self,
        repository: UserOrgRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns org_primary_id when user exists and has org."""
        user_org_id = uuid.uuid4()
        mock_user = MagicMock()
        mock_user.org_primary_id = user_org_id

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result

        result = await repository.get_user_org_id("workos_user_123")

        assert result == user_org_id

    @pytest.mark.asyncio
    async def test_get_user_org_id_raises_error_for_unknown_user(
        self,
        repository: UserOrgRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Raises UserNotFoundError when user not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        with pytest.raises(UserNotFoundError) as exc_info:
            await repository.get_user_org_id("nonexistent_user")

        assert exc_info.value.workos_user_id == "nonexistent_user"

    @pytest.mark.asyncio
    async def test_get_user_org_id_raises_error_for_user_without_org(
        self,
        repository: UserOrgRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Raises UserOrganizationRequiredError when user has no primary org."""
        mock_user = MagicMock()
        mock_user.org_primary_id = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result

        with pytest.raises(UserOrganizationRequiredError) as exc_info:
            await repository.get_user_org_id("user_without_org")

        assert exc_info.value.workos_user_id == "user_without_org"
