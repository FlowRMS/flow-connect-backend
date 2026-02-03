from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.crm.links.entity_type import EntityType

from app.graphql.inject import inject
from app.graphql.quotes.services.quote_service import QuoteService
from app.graphql.v2.core.users.strawberry.user_response import UserResponse
from app.graphql.watchers.services.entity_watcher_service import EntityWatcherService


@strawberry.type
class QuoteWatcherMutations:
    @strawberry.mutation
    @inject
    async def add_quote_watcher(
        self,
        quote_id: UUID,
        user_id: UUID,
        quote_service: Injected[QuoteService],
        watcher_service: Injected[EntityWatcherService],
    ) -> list[UserResponse]:
        _ = await quote_service.find_quote_by_id(quote_id)
        users = await watcher_service.add_watcher(EntityType.QUOTE, quote_id, user_id)
        return [UserResponse.from_orm_model(u) for u in users]

    @strawberry.mutation
    @inject
    async def remove_quote_watcher(
        self,
        quote_id: UUID,
        user_id: UUID,
        quote_service: Injected[QuoteService],
        watcher_service: Injected[EntityWatcherService],
    ) -> list[UserResponse]:
        _ = await quote_service.find_quote_by_id(quote_id)
        users = await watcher_service.remove_watcher(
            EntityType.QUOTE, quote_id, user_id
        )
        return [UserResponse.from_orm_model(u) for u in users]
