import uuid
from typing import Annotated

import strawberry
from aioinject import Injected

from app.graphql.di import inject
from app.graphql.pos.validations.services import PrefixPatternService
from app.graphql.pos.validations.strawberry import (
    CreatePrefixPatternInput,
    PrefixPatternResponse,
)


@strawberry.type
class PrefixPatternMutations:
    @strawberry.mutation()
    @inject
    async def create_prefix_pattern(
        self,
        input_data: Annotated[
            CreatePrefixPatternInput, strawberry.argument(name="input")
        ],
        service: Injected[PrefixPatternService],
    ) -> PrefixPatternResponse:
        pattern = await service.create_pattern(
            name=input_data.name,
            description=input_data.description,
        )
        return PrefixPatternResponse.from_model(pattern)

    @strawberry.mutation()
    @inject
    async def delete_prefix_pattern(
        self,
        pattern_id: Annotated[strawberry.ID, strawberry.argument(name="id")],
        service: Injected[PrefixPatternService],
    ) -> bool:
        return await service.delete_pattern(uuid.UUID(str(pattern_id)))
