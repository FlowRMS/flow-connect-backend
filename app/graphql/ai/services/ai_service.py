from commons.auth import AuthInfo

from app.graphql.ai.repositories.ai_repository import AIRepository
from app.graphql.ai.strawberry.pending_document_landing_page_response import (
    PendingDocumentLandingPageResponse,
)


class AIService:
    def __init__(
        self,
        repository: AIRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_pending_documents_landing(
        self,
        limit: int = 10,
        offset: int = 0,
    ) -> list[PendingDocumentLandingPageResponse]:
        rows = await self.repository.get_pending_documents_landing(
            limit=limit, offset=offset
        )
        return PendingDocumentLandingPageResponse.from_row_list(rows)
