from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.aliases.services.alias_service import AliasService
from app.graphql.aliases.strawberry.alias_input import AliasInput
from app.graphql.aliases.strawberry.alias_response import AliasType
from app.graphql.inject import inject


@strawberry.type
class AliasMutations:
    @strawberry.mutation
    @inject
    async def create_alias(
        self,
        input: AliasInput,
        service: Injected[AliasService],
    ) -> AliasType:
        return AliasType.from_orm_model(await service.create(input))

    @strawberry.mutation
    @inject
    async def delete_alias(
        self,
        id: UUID,
        service: Injected[AliasService],
    ) -> bool:
        return await service.delete(id)
