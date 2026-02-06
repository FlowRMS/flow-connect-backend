import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.pos.validations.exceptions import (
    PrefixPatternDuplicateError,
    PrefixPatternNotFoundError,
    UserNotAuthenticatedError,
)
from app.graphql.pos.validations.models import PrefixPattern
from app.graphql.pos.validations.services.prefix_pattern_service import (
    PrefixPatternService,
)


class TestPrefixPatternService:
    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_user_org_repository(self) -> AsyncMock:
        repo = AsyncMock()
        repo.get_user_org_id.return_value = uuid.uuid4()
        return repo

    @pytest.fixture
    def mock_auth_info(self) -> MagicMock:
        auth_info = MagicMock()
        auth_info.auth_provider_id = "user_01KEHRJ8JTMM2NZ2MQFX30C5T3"
        auth_info.flow_user_id = uuid.uuid4()
        return auth_info

    @pytest.fixture
    def service(
        self,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
        mock_auth_info: MagicMock,
    ) -> PrefixPatternService:
        return PrefixPatternService(
            repository=mock_repository,
            user_org_repository=mock_user_org_repository,
            auth_info=mock_auth_info,
        )

    @staticmethod
    def _create_mock_pattern(
        organization_id: uuid.UUID,
        name: str = "Test Pattern",
        description: str | None = "Test Description",
    ) -> MagicMock:
        mock_pattern = MagicMock(spec=PrefixPattern)
        mock_pattern.id = uuid.uuid4()
        mock_pattern.organization_id = organization_id
        mock_pattern.name = name
        mock_pattern.description = description
        return mock_pattern

    @pytest.mark.asyncio
    async def test_create_pattern_success(
        self,
        service: PrefixPatternService,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Creates pattern with name and optional description."""
        user_org_id = uuid.uuid4()
        mock_user_org_repository.get_user_org_id.return_value = user_org_id
        mock_repository.exists_by_org_and_name.return_value = False

        mock_pattern = self._create_mock_pattern(user_org_id, "My Pattern")
        mock_repository.create.return_value = mock_pattern

        result = await service.create_pattern("My Pattern")

        assert result.name == "My Pattern"
        mock_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_pattern_sets_created_by_id(
        self,
        service: PrefixPatternService,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
        mock_auth_info: MagicMock,
    ) -> None:
        """Sets created_by_id from auth_info."""
        user_org_id = uuid.uuid4()
        mock_user_org_repository.get_user_org_id.return_value = user_org_id
        mock_repository.exists_by_org_and_name.return_value = False

        mock_pattern = self._create_mock_pattern(user_org_id, "My Pattern")
        mock_repository.create.return_value = mock_pattern

        await service.create_pattern("My Pattern")

        call_args = mock_repository.create.call_args[0][0]
        assert call_args.created_by_id == mock_auth_info.flow_user_id

    @pytest.mark.asyncio
    async def test_create_pattern_duplicate_name_raises_error(
        self,
        service: PrefixPatternService,
        mock_repository: AsyncMock,
    ) -> None:
        """Raises error when name exists in org."""
        mock_repository.exists_by_org_and_name.return_value = True

        with pytest.raises(PrefixPatternDuplicateError):
            await service.create_pattern("Existing Pattern")

    @pytest.mark.asyncio
    async def test_create_pattern_unauthenticated_raises_error(
        self,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Raises error when user not authenticated."""
        mock_auth_info = MagicMock()
        mock_auth_info.auth_provider_id = None

        service = PrefixPatternService(
            repository=mock_repository,
            user_org_repository=mock_user_org_repository,
            auth_info=mock_auth_info,
        )

        with pytest.raises(UserNotAuthenticatedError):
            await service.create_pattern("My Pattern")

    @pytest.mark.asyncio
    async def test_get_all_patterns_returns_org_patterns(
        self,
        service: PrefixPatternService,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Returns all patterns for user's org."""
        user_org_id = uuid.uuid4()
        mock_user_org_repository.get_user_org_id.return_value = user_org_id

        mock_patterns = [
            self._create_mock_pattern(user_org_id, "Pattern 1"),
            self._create_mock_pattern(user_org_id, "Pattern 2"),
        ]
        mock_repository.get_all_by_org.return_value = mock_patterns

        result = await service.get_all_patterns()

        assert len(result) == 2
        mock_repository.get_all_by_org.assert_called_once_with(user_org_id)

    @pytest.mark.asyncio
    async def test_delete_pattern_success(
        self,
        service: PrefixPatternService,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Deletes pattern owned by user's org."""
        user_org_id = uuid.uuid4()
        pattern_id = uuid.uuid4()
        mock_user_org_repository.get_user_org_id.return_value = user_org_id

        mock_pattern = self._create_mock_pattern(user_org_id, "My Pattern")
        mock_pattern.id = pattern_id
        mock_repository.get_by_id.return_value = mock_pattern
        mock_repository.delete.return_value = True

        result = await service.delete_pattern(pattern_id)

        assert result is True
        mock_repository.delete.assert_called_once_with(pattern_id)

    @pytest.mark.asyncio
    async def test_delete_pattern_not_found_raises_error(
        self,
        service: PrefixPatternService,
        mock_repository: AsyncMock,
    ) -> None:
        """Raises error when pattern doesn't exist."""
        pattern_id = uuid.uuid4()
        mock_repository.get_by_id.return_value = None

        with pytest.raises(PrefixPatternNotFoundError):
            await service.delete_pattern(pattern_id)

    @pytest.mark.asyncio
    async def test_delete_pattern_wrong_org_raises_error(
        self,
        service: PrefixPatternService,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Raises error when trying to delete another org's pattern."""
        user_org_id = uuid.uuid4()
        other_org_id = uuid.uuid4()
        pattern_id = uuid.uuid4()

        mock_user_org_repository.get_user_org_id.return_value = user_org_id

        mock_pattern = self._create_mock_pattern(other_org_id, "Other Pattern")
        mock_pattern.id = pattern_id
        mock_repository.get_by_id.return_value = mock_pattern

        with pytest.raises(PrefixPatternNotFoundError):
            await service.delete_pattern(pattern_id)
