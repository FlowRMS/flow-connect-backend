import datetime

from app.graphql.pos.dashboard.strawberry.dashboard_types import (
    DashboardIssuesGlance,
    DashboardLastDeliveryGlance,
    DashboardMessagesGlance,
    DashboardPartnersGlance,
    PosDashboardGlanceResponse,
)


class TestDashboardIssuesGlance:
    def test_construction(self) -> None:
        result = DashboardIssuesGlance(blocking_sends_count=5)

        assert result.blocking_sends_count == 5

    def test_zero_count(self) -> None:
        result = DashboardIssuesGlance(blocking_sends_count=0)

        assert result.blocking_sends_count == 0


class TestDashboardPartnersGlance:
    def test_construction(self) -> None:
        result = DashboardPartnersGlance(connected_count=3, pending_count=1)

        assert result.connected_count == 3
        assert result.pending_count == 1

    def test_zero_counts(self) -> None:
        result = DashboardPartnersGlance(connected_count=0, pending_count=0)

        assert result.connected_count == 0
        assert result.pending_count == 0


class TestDashboardMessagesGlance:
    def test_construction(self) -> None:
        result = DashboardMessagesGlance(unread_count=0)

        assert result.unread_count == 0


class TestDashboardLastDeliveryGlance:
    def test_construction(self) -> None:
        date = datetime.datetime(2026, 1, 28, 14, 30, tzinfo=datetime.UTC)

        result = DashboardLastDeliveryGlance(date=date, record_count=1234)

        assert result.date == date
        assert result.record_count == 1234


class TestPosDashboardGlanceResponse:
    def test_construction_with_all_metrics(self) -> None:
        date = datetime.datetime(2026, 1, 28, 14, 30, tzinfo=datetime.UTC)
        response = PosDashboardGlanceResponse(
            issues=DashboardIssuesGlance(blocking_sends_count=2),
            partners=DashboardPartnersGlance(connected_count=3, pending_count=1),
            messages=DashboardMessagesGlance(unread_count=0),
            last_delivery=DashboardLastDeliveryGlance(
                date=date, record_count=1234
            ),
        )

        assert response.issues.blocking_sends_count == 2
        assert response.partners.connected_count == 3
        assert response.partners.pending_count == 1
        assert response.messages.unread_count == 0
        assert response.last_delivery is not None
        assert response.last_delivery.date == date
        assert response.last_delivery.record_count == 1234

    def test_construction_with_null_last_delivery(self) -> None:
        response = PosDashboardGlanceResponse(
            issues=DashboardIssuesGlance(blocking_sends_count=0),
            partners=DashboardPartnersGlance(connected_count=0, pending_count=0),
            messages=DashboardMessagesGlance(unread_count=0),
            last_delivery=None,
        )

        assert response.last_delivery is None
