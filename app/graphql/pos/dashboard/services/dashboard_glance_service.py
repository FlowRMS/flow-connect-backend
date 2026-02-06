import uuid

from commons.auth import AuthInfo

from app.graphql.connections.models import ConnectionStatus
from app.graphql.connections.repositories.connection_repository import (
    ConnectionRepository,
)
from app.graphql.connections.repositories.user_org_repository import UserOrgRepository
from app.graphql.pos.dashboard.strawberry.dashboard_types import (
    DashboardIssuesGlance,
    DashboardLastDeliveryGlance,
    DashboardMessagesGlance,
    DashboardPartnersGlance,
    PosDashboardGlanceResponse,
)
from app.graphql.pos.data_exchange.repositories import ExchangeFileRepository
from app.graphql.pos.validations.repositories import FileValidationIssueRepository


class DashboardGlanceService:
    def __init__(
        self,
        validation_issue_repository: FileValidationIssueRepository,
        connection_repository: ConnectionRepository,
        exchange_file_repository: ExchangeFileRepository,
        user_org_repository: UserOrgRepository,
        auth_info: AuthInfo,
    ) -> None:
        self.validation_issue_repository = validation_issue_repository
        self.connection_repository = connection_repository
        self.exchange_file_repository = exchange_file_repository
        self.user_org_repository = user_org_repository
        self.auth_info = auth_info

    async def _get_user_org_id(self) -> uuid.UUID:
        if self.auth_info.auth_provider_id is None:
            msg = "User not authenticated"
            raise ValueError(msg)
        return await self.user_org_repository.get_user_org_id(
            self.auth_info.auth_provider_id
        )

    async def get_glance(self) -> PosDashboardGlanceResponse:
        org_id = await self._get_user_org_id()

        blocking_count = await self.validation_issue_repository.count_blocking_issues_for_all_pending_files(
            org_id
        )
        connected_count = await self.connection_repository.count_by_status(
            org_id, ConnectionStatus.ACCEPTED
        )
        pending_count = await self.connection_repository.count_by_status(
            org_id, ConnectionStatus.PENDING
        )
        last_sent_file = await self.exchange_file_repository.get_last_sent_file(org_id)

        last_delivery = None
        if last_sent_file is not None:
            last_delivery = DashboardLastDeliveryGlance(
                date=last_sent_file.created_at,
                record_count=last_sent_file.row_count,
            )

        return PosDashboardGlanceResponse(
            issues=DashboardIssuesGlance(blocking_sends_count=blocking_count),
            partners=DashboardPartnersGlance(
                connected_count=connected_count,
                pending_count=pending_count,
            ),
            messages=DashboardMessagesGlance(unread_count=0),
            last_delivery=last_delivery,
        )
