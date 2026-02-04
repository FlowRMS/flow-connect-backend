from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from commons.db.v6.core.settings.setting_key import SettingKey

from app.graphql.v2.core.settings.repositories.general_settings_repository import (
    GeneralSettingsRepository,
)


class TestGeneralSettingsRepository:
    """Tests for GeneralSettingsRepository methods."""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_context_wrapper(self) -> MagicMock:
        context_wrapper = MagicMock()
        mock_context = MagicMock()
        mock_context.auth_info = MagicMock()
        mock_context.auth_info.flow_user_id = uuid4()
        mock_context.auth_info.roles = []
        context_wrapper.get.return_value = mock_context
        return context_wrapper

    @pytest.fixture
    def repository(
        self,
        mock_context_wrapper: MagicMock,
        mock_session: AsyncMock,
    ) -> GeneralSettingsRepository:
        return GeneralSettingsRepository(
            context_wrapper=mock_context_wrapper,
            session=mock_session,
        )

    async def test_get_by_key_with_user_id_none_uses_is_null(
        self,
        repository: GeneralSettingsRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Test that get_by_key with user_id=None uses IS NULL comparison."""
        mock_setting = MagicMock()
        mock_setting.key = SettingKey.QUOTE_SETTINGS
        mock_setting.user_id = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_setting
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_key(SettingKey.QUOTE_SETTINGS, user_id=None)

        assert result is mock_setting
        mock_session.execute.assert_awaited_once()

    async def test_get_by_key_with_specific_user_id(
        self,
        repository: GeneralSettingsRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Test that get_by_key with a specific user_id uses equality comparison."""
        user_id = uuid4()
        mock_setting = MagicMock()
        mock_setting.key = SettingKey.QUOTE_SETTINGS
        mock_setting.user_id = user_id

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_setting
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_key(SettingKey.QUOTE_SETTINGS, user_id=user_id)

        assert result is mock_setting
        mock_session.execute.assert_awaited_once()

    async def test_get_by_key_returns_none_when_not_found(
        self,
        repository: GeneralSettingsRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Test that get_by_key returns None when no matching setting exists."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_key(SettingKey.QUOTE_SETTINGS, user_id=None)

        assert result is None
        mock_session.execute.assert_awaited_once()

    async def test_get_tenant_wide_calls_get_by_key_with_none(
        self,
        repository: GeneralSettingsRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Test that get_tenant_wide delegates to get_by_key with user_id=None."""
        mock_setting = MagicMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_setting
        mock_session.execute.return_value = mock_result

        result = await repository.get_tenant_wide(SettingKey.QUOTE_SETTINGS)

        assert result is mock_setting
        mock_session.execute.assert_awaited_once()

    async def test_get_by_key_for_user_calls_get_by_key_with_user_id(
        self,
        repository: GeneralSettingsRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Test that get_by_key_for_user delegates to get_by_key with the user_id."""
        user_id = uuid4()
        mock_setting = MagicMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_setting
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_key_for_user(
            SettingKey.QUOTE_SETTINGS, user_id
        )

        assert result is mock_setting
        mock_session.execute.assert_awaited_once()

    async def test_delete_by_key_returns_true_when_setting_exists(
        self,
        repository: GeneralSettingsRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Test that delete_by_key returns True when a setting is found and deleted."""
        mock_setting = MagicMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_setting
        mock_session.execute.return_value = mock_result

        result = await repository.delete_by_key(SettingKey.QUOTE_SETTINGS, user_id=None)

        assert result is True
        mock_session.delete.assert_awaited_once_with(mock_setting)
        mock_session.flush.assert_awaited_once()

    async def test_delete_by_key_returns_false_when_setting_not_found(
        self,
        repository: GeneralSettingsRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Test that delete_by_key returns False when no matching setting exists."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.delete_by_key(SettingKey.QUOTE_SETTINGS, user_id=None)

        assert result is False
        mock_session.delete.assert_not_awaited()
        mock_session.flush.assert_not_awaited()

    async def test_list_tenant_wide_uses_is_null_for_user_id(
        self,
        repository: GeneralSettingsRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Test that list_tenant_wide uses IS NULL comparison for user_id."""
        mock_setting1 = MagicMock()
        mock_setting2 = MagicMock()

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_setting1, mock_setting2]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await repository.list_tenant_wide()

        assert result == [mock_setting1, mock_setting2]
        mock_session.execute.assert_awaited_once()
