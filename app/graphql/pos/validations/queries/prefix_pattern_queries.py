import strawberry
from aioinject import Injected

from app.graphql.di import inject
from app.graphql.pos.validations.services import PrefixPatternService
from app.graphql.pos.validations.strawberry import PrefixPatternResponse


@strawberry.type
class PrefixPatternQueries:
    @strawberry.field()
    @inject
    async def prefix_patterns(
        self,
        service: Injected[PrefixPatternService],
    ) -> list[PrefixPatternResponse]:
        patterns = await service.get_all_patterns()
        return [PrefixPatternResponse.from_model(p) for p in patterns]
