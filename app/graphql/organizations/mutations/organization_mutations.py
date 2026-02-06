from typing import Annotated

import strawberry
from aioinject import Injected

from app.graphql.di import inject
from app.graphql.organizations.services import OrganizationCreationService
from app.graphql.organizations.strawberry import (
    CreateOrganizationInput,
    OrganizationLiteResponse,
)


@strawberry.type
class OrganizationMutations:
    @strawberry.mutation()
    @inject
    async def create_organization(
        self,
        input_data: Annotated[
            CreateOrganizationInput, strawberry.argument(name="input")
        ],
        service: Injected[OrganizationCreationService],
    ) -> OrganizationLiteResponse:
        org = await service.create(input_data)
        return OrganizationLiteResponse.from_orm_model(
            org,
            flow_connect_member=False,
        )
