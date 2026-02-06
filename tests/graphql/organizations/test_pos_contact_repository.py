import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.organizations.repositories.pos_contact_repository import (
    PosContactRepository,
)


class TestPosContactRepository:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def repository(self, mock_session: AsyncMock) -> PosContactRepository:
        return PosContactRepository(session=mock_session)

    @pytest.mark.asyncio
    async def test_empty_list_returns_empty_dict(
        self,
        repository: PosContactRepository,
    ) -> None:
        """Returns empty dict when no org_ids provided."""
        result = await repository.get_pos_contacts_for_orgs([])
        assert result == {}

    @pytest.mark.asyncio
    async def test_returns_contacts_grouped_by_org(
        self,
        repository: PosContactRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Groups contacts correctly by org_id."""
        org_id = uuid.uuid4()
        user_id = uuid.uuid4()

        mock_row = MagicMock()
        mock_row.org_id = org_id
        mock_row.id = user_id
        mock_row.first_name = "John"
        mock_row.last_name = "Doe"
        mock_row.email = "john@example.com"

        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        result = await repository.get_pos_contacts_for_orgs([org_id])

        assert org_id in result
        assert result[org_id].total_count == 1
        assert len(result[org_id].contacts) == 1
        assert result[org_id].contacts[0].name == "John Doe"
        assert result[org_id].contacts[0].email == "john@example.com"

    @pytest.mark.asyncio
    async def test_limits_to_5_per_org(
        self,
        repository: PosContactRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns max 5 contacts but total_count reflects actual count."""
        org_id = uuid.uuid4()

        mock_rows = []
        for i in range(7):
            row = MagicMock()
            row.org_id = org_id
            row.id = uuid.uuid4()
            row.first_name = "User"
            row.last_name = f"{i}"
            row.email = f"user{i}@example.com"
            mock_rows.append(row)

        mock_result = MagicMock()
        mock_result.all.return_value = mock_rows
        mock_session.execute.return_value = mock_result

        result = await repository.get_pos_contacts_for_orgs([org_id])

        assert result[org_id].total_count == 7
        assert len(result[org_id].contacts) == 5
