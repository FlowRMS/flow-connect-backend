import datetime
from typing import Any

import strawberry

from app.graphql.pos.organization_alias.models import OrganizationAlias
from app.graphql.pos.organization_alias.services.organization_alias_bulk_service import (
    BulkCreateResult,
    BulkFailure,
)
from app.graphql.pos.organization_alias.services.organization_alias_service import (
    AliasGroup,
)


@strawberry.type
class OrganizationAliasResponse:
    id: strawberry.ID
    connected_org_id: strawberry.ID
    connected_org_name: str
    alias: str
    created_at: datetime.datetime | None

    @staticmethod
    def from_model(
        alias: OrganizationAlias,
        connected_org_name: str = "",
    ) -> "OrganizationAliasResponse":
        created_at: Any = alias.created_at
        return OrganizationAliasResponse(
            id=strawberry.ID(str(alias.id)),
            connected_org_id=strawberry.ID(str(alias.connected_org_id)),
            connected_org_name=connected_org_name,
            alias=alias.alias,
            created_at=created_at,
        )


@strawberry.type
class OrganizationAliasGroupResponse:
    connected_org_id: strawberry.ID
    connected_org_name: str
    aliases: list[OrganizationAliasResponse]

    @staticmethod
    def from_alias_group(group: AliasGroup) -> "OrganizationAliasGroupResponse":
        return OrganizationAliasGroupResponse(
            connected_org_id=strawberry.ID(str(group.connected_org_id)),
            connected_org_name=group.connected_org_name,
            aliases=[
                OrganizationAliasResponse.from_model(a, group.connected_org_name)
                for a in group.aliases
            ],
        )


@strawberry.type
class BulkCreateFailureResponse:
    row_number: int
    organization_name: str
    alias: str
    reason: str

    @staticmethod
    def from_failure(failure: BulkFailure) -> "BulkCreateFailureResponse":
        return BulkCreateFailureResponse(
            row_number=failure.row_number,
            organization_name=failure.organization_name,
            alias=failure.alias,
            reason=failure.reason,
        )


@strawberry.type
class BulkCreateOrganizationAliasesResponse:
    inserted_count: int
    failures: list[BulkCreateFailureResponse]

    @staticmethod
    def from_result(
        result: BulkCreateResult,
    ) -> "BulkCreateOrganizationAliasesResponse":
        return BulkCreateOrganizationAliasesResponse(
            inserted_count=result.inserted_count,
            failures=[
                BulkCreateFailureResponse.from_failure(f) for f in result.failures
            ],
        )
