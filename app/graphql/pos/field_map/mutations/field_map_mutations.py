import uuid
from typing import Annotated

import strawberry
from aioinject import Injected

from app.graphql.di import inject
from app.graphql.pos.field_map.services.field_map_service import (
    FieldInput as ServiceFieldInput,
)
from app.graphql.pos.field_map.services.field_map_service import (
    FieldMapService,
)
from app.graphql.pos.field_map.strawberry.field_map_types import (
    FieldMapResponse,
    SaveFieldMapInput,
)


@strawberry.type
class FieldMapMutations:
    @strawberry.mutation()
    @inject
    async def save_field_map(
        self,
        input_data: Annotated[SaveFieldMapInput, strawberry.argument(name="input")],
        service: Injected[FieldMapService],
    ) -> FieldMapResponse:
        org_uuid = (
            uuid.UUID(str(input_data.organization_id))
            if input_data.organization_id
            else None
        )

        # Convert GraphQL input to service input
        service_fields = [
            ServiceFieldInput(
                standard_field_key=f.standard_field_key,
                organization_field_name=f.organization_field_name,
                manufacturer=f.manufacturer,
                rep=f.rep,
                standard_field_name=f.standard_field_name,
                field_type=f.field_type,
                category=f.category,
                status=f.status,
            )
            for f in input_data.fields
        ]

        # Save using declarative approach
        updated_map = await service.save_fields(
            organization_id=org_uuid,
            map_type=input_data.map_type,
            fields=service_fields,
            direction=input_data.direction,
        )

        return FieldMapResponse.from_model(updated_map)
