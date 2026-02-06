import datetime
from enum import Enum

import strawberry

from app.graphql.pos.data_exchange.models import (
    ReceivedExchangeFile,
    ReceivedExchangeFileStatus,
)


@strawberry.enum
class ReceivedExchangeFileStatusEnum(Enum):
    NEW = "new"
    DOWNLOADED = "downloaded"

    @staticmethod
    def from_model(
        status: ReceivedExchangeFileStatus,
    ) -> "ReceivedExchangeFileStatusEnum":
        return ReceivedExchangeFileStatusEnum(status.value)


@strawberry.type
class ReceivedExchangeFileResponse:
    id: strawberry.ID
    sender_org_id: strawberry.ID
    sender_org_name: str
    file_name: str
    file_size: int
    file_type: str
    row_count: int
    reporting_period: str
    is_pos: bool
    is_pot: bool
    status: ReceivedExchangeFileStatusEnum
    received_at: datetime.datetime

    @staticmethod
    def from_model(
        file: ReceivedExchangeFile,
        sender_org_name: str = "",
    ) -> "ReceivedExchangeFileResponse":
        return ReceivedExchangeFileResponse(
            id=strawberry.ID(str(file.id)),
            sender_org_id=strawberry.ID(str(file.sender_org_id)),
            sender_org_name=sender_org_name,
            file_name=file.file_name,
            file_size=file.file_size,
            file_type=file.file_type,
            row_count=file.row_count,
            reporting_period=file.reporting_period,
            is_pos=file.is_pos,
            is_pot=file.is_pot,
            status=ReceivedExchangeFileStatusEnum(file.status),
            received_at=file.received_at,
        )


@strawberry.type
class DownloadReceivedFileResponse:
    url: str
