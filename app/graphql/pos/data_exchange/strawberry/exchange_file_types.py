import datetime
from enum import Enum

import strawberry

from app.graphql.pos.data_exchange.models import (
    ExchangeFile,
    ExchangeFileStatus,
    ExchangeFileTargetOrg,
    ValidationStatus,
)


@strawberry.enum
class ExchangeFileStatusEnum(Enum):
    PENDING = "pending"
    SENT = "sent"

    @staticmethod
    def from_model(status: ExchangeFileStatus) -> "ExchangeFileStatusEnum":
        return ExchangeFileStatusEnum(status.value)


@strawberry.enum
class ValidationStatusEnum(Enum):
    NOT_VALIDATED = "not_validated"
    VALIDATING = "validating"
    VALID = "valid"
    INVALID = "invalid"

    @staticmethod
    def from_model(status: ValidationStatus) -> "ValidationStatusEnum":
        return ValidationStatusEnum(status.value)


@strawberry.type
class ExchangeFileTargetOrgResponse:
    id: strawberry.ID
    connected_org_id: strawberry.ID

    @staticmethod
    def from_model(
        target: ExchangeFileTargetOrg,
    ) -> "ExchangeFileTargetOrgResponse":
        return ExchangeFileTargetOrgResponse(
            id=strawberry.ID(str(target.id)),
            connected_org_id=strawberry.ID(str(target.connected_org_id)),
        )


@strawberry.type
class ExchangeFileLiteResponse:
    id: strawberry.ID
    file_name: str
    file_size: int
    file_type: str
    row_count: int
    status: ExchangeFileStatusEnum
    validation_status: ValidationStatusEnum
    reporting_period: str
    is_pos: bool
    is_pot: bool
    created_at: datetime.datetime | None

    @staticmethod
    def from_model(file: ExchangeFile) -> "ExchangeFileLiteResponse":
        return ExchangeFileLiteResponse(
            id=strawberry.ID(str(file.id)),
            file_name=file.file_name,
            file_size=file.file_size,
            file_type=file.file_type,
            row_count=file.row_count,
            status=ExchangeFileStatusEnum(file.status),
            validation_status=ValidationStatusEnum(file.validation_status),
            reporting_period=file.reporting_period,
            is_pos=file.is_pos,
            is_pot=file.is_pot,
            created_at=file.created_at,
        )


@strawberry.type
class ExchangeFileResponse(ExchangeFileLiteResponse):
    target_organizations: list[ExchangeFileTargetOrgResponse]

    @staticmethod
    def from_model(file: ExchangeFile) -> "ExchangeFileResponse":
        return ExchangeFileResponse(
            id=strawberry.ID(str(file.id)),
            file_name=file.file_name,
            file_size=file.file_size,
            file_type=file.file_type,
            row_count=file.row_count,
            status=ExchangeFileStatusEnum(file.status),
            validation_status=ValidationStatusEnum(file.validation_status),
            reporting_period=file.reporting_period,
            is_pos=file.is_pos,
            is_pot=file.is_pot,
            created_at=file.created_at,
            target_organizations=[
                ExchangeFileTargetOrgResponse.from_model(t)
                for t in file.target_organizations
            ],
        )


@strawberry.type
class PendingFilesStatsResponse:
    file_count: int
    total_rows: int


@strawberry.type
class SentExchangeFilesByOrgResponse:
    connected_org_id: strawberry.ID
    connected_org_name: str
    files: list[ExchangeFileResponse]
    count: int


@strawberry.type
class SentExchangeFilesByPeriodResponse:
    reporting_period: str
    organizations: list[SentExchangeFilesByOrgResponse]


@strawberry.type
class SendPendingFilesResponse:
    success: bool
    files_sent: int
