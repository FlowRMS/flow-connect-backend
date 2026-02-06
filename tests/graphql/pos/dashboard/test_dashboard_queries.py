from unittest.mock import AsyncMock

import pytest

from app.graphql.pos.dashboard.queries.dashboard_queries import DashboardQueries
from app.graphql.pos.dashboard.strawberry.dashboard_types import (
    DashboardIssuesGlance,
    DashboardLastDeliveryGlance,
    DashboardMessagesGlance,
    DashboardPartnersGlance,
    PosDashboardGlanceResponse,
)


class TestDashboardQueries:
    @pytest.fixture
    def mock_service(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def queries(self) -> DashboardQueries:
        return DashboardQueries()

    @staticmethod
    async def _call_pos_dashboard_glance(
        queries: DashboardQueries,
        service: AsyncMock,
    ) -> PosDashboardGlanceResponse:
        unwrapped = queries.pos_dashboard_glance.__wrapped__
        return await unwrapped(queries, service=service)

    @pytest.mark.asyncio
    async def test_pos_dashboard_glance_query_returns_response(
        self,
        queries: DashboardQueries,
        mock_service: AsyncMock,
    ) -> None:
        expected = PosDashboardGlanceResponse(
            issues=DashboardIssuesGlance(blocking_sends_count=3),
            partners=DashboardPartnersGlance(connected_count=5, pending_count=2),
            messages=DashboardMessagesGlance(unread_count=0),
            last_delivery=DashboardLastDeliveryGlance(
                date="2026-01-15T00:00:00",
                record_count=1234,
            ),
        )
        mock_service.get_glance.return_value = expected

        result = await self._call_pos_dashboard_glance(queries, mock_service)

        assert result is expected
        mock_service.get_glance.assert_called_once()

    @pytest.mark.asyncio
    async def test_pos_dashboard_glance_query_null_last_delivery(
        self,
        queries: DashboardQueries,
        mock_service: AsyncMock,
    ) -> None:
        expected = PosDashboardGlanceResponse(
            issues=DashboardIssuesGlance(blocking_sends_count=0),
            partners=DashboardPartnersGlance(connected_count=0, pending_count=0),
            messages=DashboardMessagesGlance(unread_count=0),
            last_delivery=None,
        )
        mock_service.get_glance.return_value = expected

        result = await self._call_pos_dashboard_glance(queries, mock_service)

        assert result is expected
        assert result.last_delivery is None
