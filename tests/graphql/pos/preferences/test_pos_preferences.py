import uuid
from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.graphql.pos.preferences.enums import (
    PosPreferenceKey,
    RoutingMethod,
    TransferMethod,
)
from app.graphql.settings.applications.models.enums import Application
from app.graphql.settings.organization_preferences.exceptions import (
    InvalidPreferenceValueError,
)
from app.graphql.settings.organization_preferences.services.organization_preference_service import (
    OrganizationPreferenceService,
)


class TestPosPreferences:
    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_user_org_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_auth_info(self) -> MagicMock:
        auth_info = MagicMock()
        auth_info.auth_provider_id = "workos_user_123"
        return auth_info

    @pytest.fixture
    def organization_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.fixture
    def service(
        self,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
        mock_auth_info: MagicMock,
        organization_id: uuid.UUID,
    ) -> Generator[OrganizationPreferenceService, None, None]:
        mock_user_org_repository.get_user_org_id.return_value = organization_id
        svc = OrganizationPreferenceService(
            repository=mock_repository,
            user_org_repository=mock_user_org_repository,
            auth_info=mock_auth_info,
        )
        with patch.object(
            svc, "_get_organization_id", new=AsyncMock(return_value=organization_id)
        ):
            yield svc

    @pytest.mark.asyncio
    @pytest.mark.parametrize("value", [RoutingMethod.BY_COLUMN, RoutingMethod.BY_FILE])
    async def test_set_routing_method_valid_values(
        self,
        service: OrganizationPreferenceService,
        mock_repository: AsyncMock,
        value: RoutingMethod,
    ) -> None:
        mock_pref = MagicMock()
        mock_pref.preference_value = value.value
        mock_repository.upsert.return_value = mock_pref

        result = await service.set_preference(
            Application.POS,
            PosPreferenceKey.ROUTING_METHOD,
            value.value,
        )

        assert result.preference_value == value.value

    @pytest.mark.asyncio
    async def test_set_routing_method_invalid_value(
        self,
        service: OrganizationPreferenceService,
    ) -> None:
        with pytest.raises(InvalidPreferenceValueError):
            await service.set_preference(
                Application.POS,
                PosPreferenceKey.ROUTING_METHOD,
                "invalid_value",
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "value",
        [
            TransferMethod.UPLOAD_FILE,
            TransferMethod.API,
            TransferMethod.SFTP,
            TransferMethod.EMAIL,
        ],
    )
    async def test_set_receiving_method_valid_values(
        self,
        service: OrganizationPreferenceService,
        mock_repository: AsyncMock,
        value: TransferMethod,
    ) -> None:
        mock_pref = MagicMock()
        mock_pref.preference_value = value.value
        mock_repository.upsert.return_value = mock_pref

        result = await service.set_preference(
            Application.POS,
            PosPreferenceKey.RECEIVING_METHOD,
            value.value,
        )

        assert result.preference_value == value.value

    @pytest.mark.asyncio
    async def test_set_receiving_method_invalid_value(
        self,
        service: OrganizationPreferenceService,
    ) -> None:
        with pytest.raises(InvalidPreferenceValueError):
            await service.set_preference(
                Application.POS,
                PosPreferenceKey.RECEIVING_METHOD,
                "invalid_value",
            )

    @pytest.mark.asyncio
    async def test_set_manufacturer_column_accepts_any_text(
        self,
        service: OrganizationPreferenceService,
        mock_repository: AsyncMock,
    ) -> None:
        mock_pref = MagicMock()
        mock_pref.preference_value = "Brand"
        mock_repository.upsert.return_value = mock_pref

        result = await service.set_preference(
            Application.POS,
            PosPreferenceKey.MANUFACTURER_COLUMN,
            "Brand",
        )

        assert result.preference_value == "Brand"
