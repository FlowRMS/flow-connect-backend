import uuid
from dataclasses import dataclass

from commons.auth import AuthInfo

from app.graphql.connections.repositories.user_org_repository import UserOrgRepository
from app.graphql.pos.organization_alias.exceptions import (
    AliasAlreadyExistsError,
    OrganizationNotConnectedError,
)
from app.graphql.pos.organization_alias.repositories import OrganizationAliasRepository
from app.graphql.pos.organization_alias.services.organization_alias_csv_parser import (
    parse_csv,
)
from app.graphql.pos.organization_alias.services.organization_alias_service import (
    OrganizationAliasService,
)


@dataclass
class BulkFailure:
    row_number: int
    organization_name: str
    alias: str
    reason: str


@dataclass
class BulkCreateResult:
    inserted_count: int
    failures: list[BulkFailure]


class OrganizationAliasBulkService:
    def __init__(
        self,
        alias_service: OrganizationAliasService,
        repository: OrganizationAliasRepository,
        user_org_repository: UserOrgRepository,
        auth_info: AuthInfo,
    ) -> None:
        self.alias_service = alias_service
        self.repository = repository
        self.user_org_repository = user_org_repository
        self.auth_info = auth_info

    async def _get_user_org_id(self) -> uuid.UUID:
        if self.auth_info.auth_provider_id is None:
            raise OrganizationNotConnectedError("User not authenticated")
        return await self.user_org_repository.get_user_org_id(
            self.auth_info.auth_provider_id
        )

    async def bulk_create_from_csv(self, content: bytes) -> BulkCreateResult:
        rows = parse_csv(content)

        user_org_id = await self._get_user_org_id()

        org_names = [row.organization_name for row in rows if row.organization_name]
        orgs_by_name = await self.repository.get_connected_orgs_by_name(
            user_org_id, org_names
        )

        inserted_count = 0
        failures: list[BulkFailure] = []

        for row in rows:
            if not row.alias:
                failures.append(
                    BulkFailure(
                        row_number=row.row_number,
                        organization_name=row.organization_name,
                        alias=row.alias,
                        reason="Missing alias value",
                    )
                )
                continue

            org = orgs_by_name.get(row.organization_name.lower())
            if org is None:
                failures.append(
                    BulkFailure(
                        row_number=row.row_number,
                        organization_name=row.organization_name,
                        alias=row.alias,
                        reason="Organization not found",
                    )
                )
                continue

            try:
                await self.alias_service.create_alias(org.id, row.alias)
                inserted_count += 1
            except OrganizationNotConnectedError:
                failures.append(
                    BulkFailure(
                        row_number=row.row_number,
                        organization_name=row.organization_name,
                        alias=row.alias,
                        reason="Organization not connected",
                    )
                )
            except AliasAlreadyExistsError:
                failures.append(
                    BulkFailure(
                        row_number=row.row_number,
                        organization_name=row.organization_name,
                        alias=row.alias,
                        reason="Alias already exists",
                    )
                )

        return BulkCreateResult(inserted_count=inserted_count, failures=failures)
