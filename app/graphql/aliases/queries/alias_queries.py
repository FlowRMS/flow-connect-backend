from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.core.aliases.alias_entity_type import AliasEntityType
from commons.db.v6.core.aliases.alias_sub_type import AliasSubType

from app.graphql.aliases.services.alias_service import AliasService
from app.graphql.aliases.strawberry.alias_response import AliasType
from app.graphql.inject import inject


@strawberry.type
class AliasQueries:
    @strawberry.field
    @inject
    async def alias(
        self,
        id: UUID,
        service: Injected[AliasService],
    ) -> AliasType:
        return AliasType.from_orm_model(await service.get_by_id(id))

    @strawberry.field
    @inject
    async def aliases_by_entity(
        self,
        entity_id: UUID,
        entity_type: AliasEntityType,
        service: Injected[AliasService],
        sub_type: AliasSubType | None = None,
    ) -> list[AliasType]:
        aliases = await service.get_by_entity(entity_id, entity_type, sub_type)
        return AliasType.from_orm_model_list(aliases)

    @strawberry.field
    @inject
    async def alias_search(
        self,
        search_term: str,
        service: Injected[AliasService],
        entity_type: AliasEntityType | None = None,
        sub_type: AliasSubType | None = None,
        limit: int = 20,
    ) -> list[AliasType]:
        aliases = await service.search_by_alias(
            search_term, entity_type, sub_type, limit
        )
        return AliasType.from_orm_model_list(aliases)
