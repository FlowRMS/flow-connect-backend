import strawberry
from aioinject import Injected

from app.graphql.ai.services.ai_service import AIService
from app.graphql.ai.strawberry.pending_document_landing_page_response import (
    PendingDocumentLandingPageResponse,
)
from app.graphql.inject import inject


@strawberry.type
class AIQueries:
    @strawberry.field
    @inject
    async def pending_documents_landing(
        self,
        service: Injected[AIService],
        limit: int = 10,
        offset: int = 0,
    ) -> list[PendingDocumentLandingPageResponse]:
        return await service.get_pending_documents_landing(limit=limit, offset=offset)
