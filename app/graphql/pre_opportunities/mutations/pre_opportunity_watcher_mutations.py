from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.crm.links.entity_type import EntityType

from app.graphql.inject import inject
from app.graphql.pre_opportunities.services.pre_opportunities_service import (
    PreOpportunitiesService,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse
from app.graphql.watchers.services.entity_watcher_service import EntityWatcherService


@strawberry.type
class PreOpportunityWatcherMutations:
    @strawberry.mutation
    @inject
    async def add_pre_opportunity_watcher(
        self,
        pre_opportunity_id: UUID,
        user_id: UUID,
        pre_opportunities_service: Injected[PreOpportunitiesService],
        watcher_service: Injected[EntityWatcherService],
    ) -> list[UserResponse]:
        _ = await pre_opportunities_service.get_pre_opportunity(pre_opportunity_id)
        users = await watcher_service.add_watcher(
            EntityType.PRE_OPPORTUNITY, pre_opportunity_id, user_id
        )
        return [UserResponse.from_orm_model(u) for u in users]

    @strawberry.mutation
    @inject
    async def remove_pre_opportunity_watcher(
        self,
        pre_opportunity_id: UUID,
        user_id: UUID,
        pre_opportunities_service: Injected[PreOpportunitiesService],
        watcher_service: Injected[EntityWatcherService],
    ) -> list[UserResponse]:
        _ = await pre_opportunities_service.get_pre_opportunity(pre_opportunity_id)
        users = await watcher_service.remove_watcher(
            EntityType.PRE_OPPORTUNITY, pre_opportunity_id, user_id
        )
        return [UserResponse.from_orm_model(u) for u in users]
