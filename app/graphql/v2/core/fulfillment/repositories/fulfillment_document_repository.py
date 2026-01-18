from uuid import UUID

from commons.db.v6.fulfillment import FulfillmentDocument
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class FulfillmentDocumentRepository(BaseRepository[FulfillmentDocument]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, FulfillmentDocument)

    async def find_by_fulfillment_order(
        self, fulfillment_order_id: UUID
    ) -> list[FulfillmentDocument]:
        stmt = (
            select(FulfillmentDocument)
            .options(selectinload(FulfillmentDocument.uploaded_by_user))
            .where(FulfillmentDocument.fulfillment_order_id == fulfillment_order_id)
            .order_by(FulfillmentDocument.uploaded_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_with_user(self, document_id: UUID) -> FulfillmentDocument | None:
        """Get a document by ID with uploaded_by_user relationship loaded."""
        stmt = (
            select(FulfillmentDocument)
            .options(selectinload(FulfillmentDocument.uploaded_by_user))
            .where(FulfillmentDocument.id == document_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
