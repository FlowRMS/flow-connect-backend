import strawberry
from aioinject import Injected

from app.graphql.di import inject
from app.graphql.pos.dashboard.services.dashboard_glance_service import (
    DashboardGlanceService,
)
from app.graphql.pos.dashboard.strawberry.dashboard_types import (
    PosDashboardGlanceResponse,
)


@strawberry.type
class DashboardQueries:
    @strawberry.field()
    @inject
    async def pos_dashboard_glance(
        self,
        service: Injected[DashboardGlanceService],
    ) -> PosDashboardGlanceResponse:
        return await service.get_glance()
