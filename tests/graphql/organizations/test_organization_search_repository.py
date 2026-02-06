import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.organizations.models import OrgType
from app.graphql.organizations.repositories.organization_search_repository import (
    OrganizationSearchRepository,
)


class TestOrganizationSearchRepositoryOrgTypeFilter:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        mock_result = MagicMock()
        mock_result.all.return_value = []
        session.execute.return_value = mock_result
        return session

    @pytest.fixture
    def repository(self, mock_session: AsyncMock) -> OrganizationSearchRepository:
        return OrganizationSearchRepository(session=mock_session)

    @pytest.fixture
    def user_org_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @staticmethod
    def _get_query_string(mock_session: AsyncMock) -> str:
        call_args = mock_session.execute.call_args
        stmt = call_args[0][0]
        return str(stmt.compile(compile_kwargs={"literal_binds": True}))

    @pytest.mark.asyncio
    async def test_search_filters_by_manufacturer_type(
        self,
        repository: OrganizationSearchRepository,
        mock_session: AsyncMock,
        user_org_id: uuid.UUID,
    ) -> None:
        """When org_type=MANUFACTURER, query filters for manufacturer orgs."""
        await repository.search(
            "test",
            org_type=OrgType.MANUFACTURER,
            user_org_id=user_org_id,
        )

        query = self._get_query_string(mock_session)
        assert OrgType.MANUFACTURER.value in query

    @pytest.mark.asyncio
    async def test_search_filters_by_distributor_type(
        self,
        repository: OrganizationSearchRepository,
        mock_session: AsyncMock,
        user_org_id: uuid.UUID,
    ) -> None:
        """When org_type=DISTRIBUTOR, query filters for distributor orgs."""
        await repository.search(
            "test",
            org_type=OrgType.DISTRIBUTOR,
            user_org_id=user_org_id,
        )

        query = self._get_query_string(mock_session)
        assert OrgType.DISTRIBUTOR.value in query

    @pytest.mark.asyncio
    async def test_search_different_types_produce_different_queries(
        self,
        repository: OrganizationSearchRepository,
        mock_session: AsyncMock,
        user_org_id: uuid.UUID,
    ) -> None:
        """Different org_types produce different SQL queries."""
        await repository.search(
            "test",
            org_type=OrgType.MANUFACTURER,
            user_org_id=user_org_id,
        )
        manufacturer_query = self._get_query_string(mock_session)

        await repository.search(
            "test",
            org_type=OrgType.DISTRIBUTOR,
            user_org_id=user_org_id,
        )
        distributor_query = self._get_query_string(mock_session)

        assert OrgType.MANUFACTURER.value in manufacturer_query
        assert OrgType.DISTRIBUTOR.value in distributor_query
        assert OrgType.MANUFACTURER.value not in distributor_query
        assert OrgType.DISTRIBUTOR.value not in manufacturer_query
