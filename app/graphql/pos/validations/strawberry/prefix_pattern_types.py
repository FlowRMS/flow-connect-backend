import datetime
from typing import Any

import strawberry

from app.graphql.pos.validations.models import PrefixPattern


@strawberry.type
class PrefixPatternResponse:
    id: strawberry.ID
    name: str
    description: str | None
    created_at: datetime.datetime | None

    @staticmethod
    def from_model(pattern: PrefixPattern) -> "PrefixPatternResponse":
        created_at: Any = pattern.created_at
        return PrefixPatternResponse(
            id=strawberry.ID(str(pattern.id)),
            name=pattern.name,
            description=pattern.description,
            created_at=created_at,
        )
