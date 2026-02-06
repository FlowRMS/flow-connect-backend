import uuid
from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.graphql.settings.applications.models.enums import Application
from app.graphql.settings.organization_preferences.exceptions import (
    InvalidApplicationError,
    InvalidPreferenceValueError,
)
from app.graphql.settings.organization_preferences.models.organization_preference import (
    OrganizationPreference,
)
from app.graphql.settings.organization_preferences.services.organization_preference_service import (
    OrganizationPreferenceService,
)


@pytest.fixture
def mock_repository() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_user_org_repository() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_auth_info() -> MagicMock:
    auth_info = MagicMock()
    auth_info.auth_provider_id = "workos_user_123"
    return auth_info


@pytest.fixture
def organization_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def service(
    mock_repository: MagicMock,
    mock_user_org_repository: MagicMock,
    mock_auth_info: MagicMock,
    organization_id: uuid.UUID,
) -> Generator[OrganizationPreferenceService, None, None]:
    mock_user_org_repository.get_user_org_id = AsyncMock(return_value=organization_id)
    svc = OrganizationPreferenceService(
        repository=mock_repository,
        user_org_repository=mock_user_org_repository,
        auth_info=mock_auth_info,
    )
    with patch.object(
        svc, "_get_organization_id", new=AsyncMock(return_value=organization_id)
    ):
        yield svc


class TestGetPreference:
    @pytest.mark.asyncio
    async def test_returns_value_when_preference_exists(
        self,
        service: OrganizationPreferenceService,
        mock_repository: MagicMock,
        organization_id: uuid.UUID,
    ) -> None:
        pref = OrganizationPreference(
            organization_id=organization_id,
            application="POS",
            preference_key="send_method",
            preference_value="email",
        )
        mock_repository.get_by_org_application_key = AsyncMock(return_value=pref)

        result = await service.get_preference(Application.POS, "send_method")

        assert result == "email"

    @pytest.mark.asyncio
    async def test_returns_none_when_preference_not_found(
        self,
        service: OrganizationPreferenceService,
        mock_repository: MagicMock,
    ) -> None:
        mock_repository.get_by_org_application_key = AsyncMock(return_value=None)

        result = await service.get_preference(Application.POS, "nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_for_null_value(
        self,
        service: OrganizationPreferenceService,
        mock_repository: MagicMock,
        organization_id: uuid.UUID,
    ) -> None:
        pref = OrganizationPreference(
            organization_id=organization_id,
            application="POS",
            preference_key="send_method",
            preference_value=None,
        )
        mock_repository.get_by_org_application_key = AsyncMock(return_value=pref)

        result = await service.get_preference(Application.POS, "send_method")

        assert result is None


class TestGetPreferencesByApplication:
    @pytest.mark.asyncio
    async def test_returns_list_for_application(
        self,
        service: OrganizationPreferenceService,
        mock_repository: MagicMock,
        organization_id: uuid.UUID,
    ) -> None:
        prefs = [
            OrganizationPreference(
                organization_id=organization_id,
                application="POS",
                preference_key="send_method",
                preference_value="email",
            ),
        ]
        mock_repository.get_by_org_and_application = AsyncMock(return_value=prefs)

        result = await service.get_preferences_by_application(Application.POS)

        assert result == prefs


class TestGetAllPreferences:
    @pytest.mark.asyncio
    async def test_groups_by_application(
        self,
        service: OrganizationPreferenceService,
        mock_repository: MagicMock,
        organization_id: uuid.UUID,
    ) -> None:
        prefs = [
            OrganizationPreference(
                organization_id=organization_id,
                application="POS",
                preference_key="send_method",
                preference_value="email",
            ),
            OrganizationPreference(
                organization_id=organization_id,
                application="POS",
                preference_key="routing_method",
                preference_value="auto",
            ),
        ]
        mock_repository.get_all_by_org = AsyncMock(return_value=prefs)

        result = await service.get_all_preferences()

        assert "POS" in result
        assert len(result["POS"]) == 2


class TestSetPreference:
    @pytest.mark.asyncio
    async def test_creates_new_preference(
        self,
        service: OrganizationPreferenceService,
        mock_repository: MagicMock,
        organization_id: uuid.UUID,
    ) -> None:
        expected = OrganizationPreference(
            organization_id=organization_id,
            application="POS",
            preference_key="manufacturer_column",
            preference_value="Brand",
        )
        mock_repository.upsert = AsyncMock(return_value=expected)

        result = await service.set_preference(
            Application.POS,
            "manufacturer_column",
            "Brand",
        )

        assert result == expected
        mock_repository.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_updates_existing_preference(
        self,
        service: OrganizationPreferenceService,
        mock_repository: MagicMock,
        organization_id: uuid.UUID,
    ) -> None:
        updated = OrganizationPreference(
            organization_id=organization_id,
            application="POS",
            preference_key="manufacturer_column",
            preference_value="NewBrand",
        )
        mock_repository.upsert = AsyncMock(return_value=updated)

        result = await service.set_preference(
            Application.POS,
            "manufacturer_column",
            "NewBrand",
        )

        assert result.preference_value == "NewBrand"

    @pytest.mark.asyncio
    async def test_resets_with_none_value(
        self,
        service: OrganizationPreferenceService,
        mock_repository: MagicMock,
        organization_id: uuid.UUID,
    ) -> None:
        reset_pref = OrganizationPreference(
            organization_id=organization_id,
            application="POS",
            preference_key="manufacturer_column",
            preference_value=None,
        )
        mock_repository.upsert = AsyncMock(return_value=reset_pref)

        result = await service.set_preference(
            Application.POS,
            "manufacturer_column",
            None,
        )

        assert result.preference_value is None

    @pytest.mark.asyncio
    async def test_invalid_application_raises_error(
        self,
        service: OrganizationPreferenceService,
    ) -> None:
        with pytest.raises(InvalidApplicationError):
            await service.set_preference("INVALID_APP", "key", "value")

    @pytest.mark.asyncio
    async def test_invalid_preference_value_raises_error(
        self,
        service: OrganizationPreferenceService,
        mock_repository: MagicMock,
    ) -> None:
        with pytest.raises(InvalidPreferenceValueError):
            await service.set_preference(Application.POS, "send_method", "invalid")
