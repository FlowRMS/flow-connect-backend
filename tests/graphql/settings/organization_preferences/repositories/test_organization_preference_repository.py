import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.settings.organization_preferences.models.organization_preference import (
    OrganizationPreference,
)
from app.graphql.settings.organization_preferences.repositories.organization_preference_repository import (
    OrganizationPreferenceRepository,
)


@pytest.fixture
def mock_session() -> MagicMock:
    return MagicMock()


@pytest.fixture
def repository(mock_session: MagicMock) -> OrganizationPreferenceRepository:
    return OrganizationPreferenceRepository(session=mock_session)


class TestGetByOrgApplicationKey:
    @pytest.mark.asyncio
    async def test_returns_preference_when_found(
        self,
        repository: OrganizationPreferenceRepository,
        mock_session: MagicMock,
    ) -> None:
        org_id = uuid.uuid4()
        expected_pref = OrganizationPreference(
            organization_id=org_id,
            application="POS",
            preference_key="send_method",
            preference_value="email",
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = expected_pref
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repository.get_by_org_application_key(
            organization_id=org_id,
            application="POS",
            key="send_method",
        )

        assert result == expected_pref
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(
        self,
        repository: OrganizationPreferenceRepository,
        mock_session: MagicMock,
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repository.get_by_org_application_key(
            organization_id=uuid.uuid4(),
            application="POS",
            key="nonexistent",
        )

        assert result is None


class TestGetByOrgAndApplication:
    @pytest.mark.asyncio
    async def test_returns_list_of_preferences(
        self,
        repository: OrganizationPreferenceRepository,
        mock_session: MagicMock,
    ) -> None:
        org_id = uuid.uuid4()
        prefs = [
            OrganizationPreference(
                organization_id=org_id,
                application="POS",
                preference_key="send_method",
                preference_value="email",
            ),
            OrganizationPreference(
                organization_id=org_id,
                application="POS",
                preference_key="routing_method",
                preference_value="auto",
            ),
        ]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = prefs
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repository.get_by_org_and_application(
            organization_id=org_id,
            application="POS",
        )

        assert result == prefs
        assert len(result) == 2


class TestGetAllByOrg:
    @pytest.mark.asyncio
    async def test_returns_all_preferences_for_org(
        self,
        repository: OrganizationPreferenceRepository,
        mock_session: MagicMock,
    ) -> None:
        org_id = uuid.uuid4()
        prefs = [
            OrganizationPreference(
                organization_id=org_id,
                application="POS",
                preference_key="send_method",
                preference_value="email",
            ),
        ]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = prefs
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repository.get_all_by_org(organization_id=org_id)

        assert result == prefs


class TestUpsert:
    @pytest.mark.asyncio
    async def test_creates_new_preference(
        self,
        repository: OrganizationPreferenceRepository,
        mock_session: MagicMock,
    ) -> None:
        org_id = uuid.uuid4()
        expected_pref = OrganizationPreference(
            organization_id=org_id,
            application="POS",
            preference_key="send_method",
            preference_value="email",
        )
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = expected_pref
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repository.upsert(
            organization_id=org_id,
            application="POS",
            key="send_method",
            value="email",
        )

        assert result == expected_pref
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_updates_existing_preference(
        self,
        repository: OrganizationPreferenceRepository,
        mock_session: MagicMock,
    ) -> None:
        org_id = uuid.uuid4()
        updated_pref = OrganizationPreference(
            organization_id=org_id,
            application="POS",
            preference_key="send_method",
            preference_value="fax",
        )
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = updated_pref
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repository.upsert(
            organization_id=org_id,
            application="POS",
            key="send_method",
            value="fax",
        )

        assert result.preference_value == "fax"
