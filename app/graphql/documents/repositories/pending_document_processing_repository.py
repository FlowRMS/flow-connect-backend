from uuid import UUID

from commons.db.v6 import RbacResourceEnum
from commons.db.v6.ai.documents.pending_document_processing import (
    PendingDocumentProcessing,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class PendingDocumentProcessingRepository(BaseRepository[PendingDocumentProcessing]):
    rbac_resource: RbacResourceEnum | None = None

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, PendingDocumentProcessing)

    async def get_by_pending_document_id(
        self,
        pending_document_id: UUID,
    ) -> list[PendingDocumentProcessing]:
        stmt = select(PendingDocumentProcessing).where(
            PendingDocumentProcessing.pending_document_id == pending_document_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
