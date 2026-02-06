import uuid
from typing import Annotated, Any

import strawberry
from aioinject import Injected
from strawberry.file_uploads import Upload

from app.graphql.di import inject
from app.graphql.pos.organization_alias.services.organization_alias_bulk_service import (
    OrganizationAliasBulkService,
)
from app.graphql.pos.organization_alias.services.organization_alias_service import (
    OrganizationAliasService,
)
from app.graphql.pos.organization_alias.strawberry.organization_alias_inputs import (
    CreateOrganizationAliasInput,
)
from app.graphql.pos.organization_alias.strawberry.organization_alias_types import (
    BulkCreateOrganizationAliasesResponse,
    OrganizationAliasResponse,
)


@strawberry.type
class OrganizationAliasMutations:
    @strawberry.mutation()
    @inject
    async def create_organization_alias(
        self,
        input_data: Annotated[
            CreateOrganizationAliasInput, strawberry.argument(name="input")
        ],
        service: Injected[OrganizationAliasService],
    ) -> OrganizationAliasResponse:
        alias = await service.create_alias(
            connected_org_id=uuid.UUID(str(input_data.connected_org_id)),
            alias=input_data.alias,
        )
        return OrganizationAliasResponse.from_model(alias)

    @strawberry.mutation()
    @inject
    async def delete_organization_alias(
        self,
        alias_id: Annotated[strawberry.ID, strawberry.argument(name="id")],
        service: Injected[OrganizationAliasService],
    ) -> bool:
        return await service.delete_alias(uuid.UUID(str(alias_id)))

    @strawberry.mutation()
    @inject
    async def bulk_spreadsheet_create_organization_aliases(
        self,
        file: Upload,
        service: Injected[OrganizationAliasBulkService],
    ) -> BulkCreateOrganizationAliasesResponse:
        upload_file: Any = file
        file_content = await upload_file.read()
        result = await service.bulk_create_from_csv(file_content)
        return BulkCreateOrganizationAliasesResponse.from_result(result)
