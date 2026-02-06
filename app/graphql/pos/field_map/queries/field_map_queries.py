import uuid

import strawberry
from aioinject import Injected

from app.graphql.di import inject
from app.graphql.pos.field_map.models.field_map_enums import (
    FieldMapDirection,
    FieldMapType,
)
from app.graphql.pos.field_map.repositories.field_map_repository import (
    FieldMapRepository,
)
from app.graphql.pos.field_map.strawberry.field_map_types import (
    FieldMapResponse,
)


@strawberry.type
class FieldMapQueries:
    @strawberry.field()
    @inject
    async def field_map(
        self,
        map_type: FieldMapType,
        repository: Injected[FieldMapRepository],
        organization_id: strawberry.ID | None = None,
        direction: FieldMapDirection = FieldMapDirection.SEND,
    ) -> FieldMapResponse:
        org_uuid = uuid.UUID(str(organization_id)) if organization_id else None
        field_map = await repository.get_by_org_and_type(org_uuid, map_type, direction)
        if not field_map:
            return FieldMapResponse.from_defaults(org_uuid, map_type, direction)
        return FieldMapResponse.from_model(field_map)
