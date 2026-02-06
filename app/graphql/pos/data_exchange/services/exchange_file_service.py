import hashlib
import io
import uuid
from dataclasses import dataclass, field

from commons.auth import AuthInfo
from commons.s3.service import S3Service

from app.graphql.connections.repositories.user_org_repository import UserOrgRepository
from app.graphql.organizations.repositories import OrganizationSearchRepository
from app.graphql.pos.data_exchange.exceptions import (
    CannotDeleteSentFileError,
    DuplicateFileForTargetError,
    ExchangeFileError,
    ExchangeFileNotFoundError,
    HasBlockingValidationIssuesError,
    NoPendingFilesError,
)
from app.graphql.pos.data_exchange.models import (
    ExchangeFile,
    ExchangeFileStatus,
    ExchangeFileTargetOrg,
)
from app.graphql.pos.data_exchange.repositories import ExchangeFileRepository
from app.graphql.pos.data_exchange.services.cross_tenant_delivery_service import (
    CrossTenantDeliveryService,
)
from app.graphql.pos.data_exchange.services.file_validators import (
    count_rows,
    validate_file_type,
)
from app.graphql.pos.validations.repositories import FileValidationIssueRepository
from app.graphql.pos.validations.services.validation_task import trigger_validation_task


@dataclass
class SentFilesByOrg:
    connected_org_id: uuid.UUID
    connected_org_name: str
    files: list[ExchangeFile] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.files)


@dataclass
class SentFilesByPeriod:
    reporting_period: str
    organizations: list[SentFilesByOrg] = field(default_factory=list)


class ExchangeFileService:
    def __init__(
        self,
        repository: ExchangeFileRepository,
        s3_service: S3Service,
        user_org_repository: UserOrgRepository,
        org_search_repository: OrganizationSearchRepository,
        validation_issue_repository: FileValidationIssueRepository,
        auth_info: AuthInfo,
        delivery_service: CrossTenantDeliveryService | None = None,
    ) -> None:
        self.repository = repository
        self.s3_service = s3_service
        self.user_org_repository = user_org_repository
        self.org_search_repository = org_search_repository
        self.validation_issue_repository = validation_issue_repository
        self.auth_info = auth_info
        self.delivery_service = delivery_service

    async def _get_user_org_id(self) -> uuid.UUID:
        if self.auth_info.auth_provider_id is None:
            raise ExchangeFileError("User not authenticated")
        return await self.user_org_repository.get_user_org_id(
            self.auth_info.auth_provider_id
        )

    async def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        reporting_period: str,
        is_pos: bool,
        is_pot: bool,
        target_org_ids: list[uuid.UUID],
    ) -> ExchangeFile:
        org_id = await self._get_user_org_id()
        file_type = validate_file_type(file_name)
        file_sha = hashlib.sha256(file_content).hexdigest()

        has_duplicate = await self.repository.has_pending_with_sha_and_target(
            org_id=org_id,
            file_sha=file_sha,
            target_org_ids=target_org_ids,
        )
        if has_duplicate:
            raise DuplicateFileForTargetError(
                "A pending file with the same content already targets "
                "one of the selected organizations"
            )

        row_count = count_rows(file_content, file_type)
        s3_key = f"exchange-files/{org_id}/{file_sha}.{file_type}"

        await self.s3_service.upload(
            key=s3_key,
            file_obj=io.BytesIO(file_content),
        )

        exchange_file = ExchangeFile(
            org_id=org_id,
            s3_key=s3_key,
            file_name=file_name,
            file_size=len(file_content),
            file_sha=file_sha,
            file_type=file_type,
            row_count=row_count,
            reporting_period=reporting_period,
            is_pos=is_pos,
            is_pot=is_pot,
            status=ExchangeFileStatus.PENDING.value,
        )
        exchange_file.created_by_id = self.auth_info.flow_user_id

        for target_org_id in target_org_ids:
            target = ExchangeFileTargetOrg(connected_org_id=target_org_id)
            exchange_file.target_organizations.append(target)

        created_file = await self.repository.create(exchange_file)
        trigger_validation_task(created_file.id)
        return created_file

    async def delete_file(self, file_id: uuid.UUID) -> bool:
        org_id = await self._get_user_org_id()
        file = await self.repository.get_by_id(file_id)
        if file is None or file.org_id != org_id:
            raise ExchangeFileNotFoundError(f"Exchange file {file_id} not found")

        if file.status == ExchangeFileStatus.SENT.value:
            raise CannotDeleteSentFileError("Cannot delete a file that has been sent")

        return await self.repository.delete(file_id)

    async def list_pending_files(self) -> list[ExchangeFile]:
        org_id = await self._get_user_org_id()
        return await self.repository.list_pending_for_org(org_id)

    async def get_pending_stats(self) -> tuple[int, int]:
        org_id = await self._get_user_org_id()
        return await self.repository.get_pending_stats(org_id)

    async def get_sent_files_grouped(
        self,
        *,
        period: str | None = None,
        organizations: list[uuid.UUID] | None = None,
        is_pos: bool | None = None,
        is_pot: bool | None = None,
    ) -> list[SentFilesByPeriod]:
        org_id = await self._get_user_org_id()

        files = await self.repository.list_sent_files(
            org_id,
            period=period,
            organizations=organizations,
            is_pos=is_pos,
            is_pot=is_pot,
        )

        if not files:
            return []

        all_target_org_ids = {
            target.connected_org_id for f in files for target in f.target_organizations
        }
        org_names = await self.org_search_repository.get_names_by_ids(
            list(all_target_org_ids)
        )

        periods: dict[str, dict[uuid.UUID, SentFilesByOrg]] = {}

        for file in files:
            if file.reporting_period not in periods:
                periods[file.reporting_period] = {}

            period_orgs = periods[file.reporting_period]

            for target in file.target_organizations:
                target_org_id = target.connected_org_id
                if target_org_id not in period_orgs:
                    period_orgs[target_org_id] = SentFilesByOrg(
                        connected_org_id=target_org_id,
                        connected_org_name=org_names.get(target_org_id, ""),
                    )
                period_orgs[target_org_id].files.append(file)

        return [
            SentFilesByPeriod(
                reporting_period=period_name,
                organizations=list(org_groups.values()),
            )
            for period_name, org_groups in periods.items()
        ]

    async def send_pending_files(self) -> int:
        org_id = await self._get_user_org_id()

        has_blocking = await self.validation_issue_repository.has_blocking_issues_for_pending_files(
            org_id
        )
        if has_blocking:
            raise HasBlockingValidationIssuesError(
                "Cannot send files with blocking validation issues"
            )

        # Query pending files before updating status (needed for delivery)
        pending_files = await self.repository.list_pending_for_org(org_id)

        count = await self.repository.update_pending_to_sent(org_id)
        if count == 0:
            raise NoPendingFilesError("No pending files to send")

        # Deliver files to target organizations' tenant databases
        if self.delivery_service is not None and pending_files:
            await self.delivery_service.deliver_files(pending_files)

        return count
