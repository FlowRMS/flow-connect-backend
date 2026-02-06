import datetime

import strawberry


@strawberry.type
class DashboardIssuesGlance:
    blocking_sends_count: int


@strawberry.type
class DashboardPartnersGlance:
    connected_count: int
    pending_count: int


@strawberry.type
class DashboardMessagesGlance:
    unread_count: int


@strawberry.type
class DashboardLastDeliveryGlance:
    date: datetime.datetime
    record_count: int


@strawberry.type
class PosDashboardGlanceResponse:
    issues: DashboardIssuesGlance
    partners: DashboardPartnersGlance
    messages: DashboardMessagesGlance
    last_delivery: DashboardLastDeliveryGlance | None
