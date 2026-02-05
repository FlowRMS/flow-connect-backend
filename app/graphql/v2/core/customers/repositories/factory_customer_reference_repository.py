from uuid import UUID

from commons.db.v6.core.customers.factory_customer_reference import (
    FactoryCustomerReference,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class FactoryCustomerReferenceRepository(BaseRepository[FactoryCustomerReference]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, FactoryCustomerReference)

    async def list_by_factory(
        self,
        factory_id: UUID,
    ) -> list[FactoryCustomerReference]:
        stmt = (
            select(FactoryCustomerReference)
            .where(FactoryCustomerReference.factory_id == factory_id)
            .options(
                joinedload(FactoryCustomerReference.factory),
                joinedload(FactoryCustomerReference.customer),
                joinedload(FactoryCustomerReference.address),
            )
            .order_by(FactoryCustomerReference.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def get_by_customer_and_factory(
        self,
        customer_id: UUID,
        factory_id: UUID,
    ) -> FactoryCustomerReference | None:
        stmt = (
            select(FactoryCustomerReference)
            .where(
                FactoryCustomerReference.customer_id == customer_id,
                FactoryCustomerReference.factory_id == factory_id,
            )
            .options(
                joinedload(FactoryCustomerReference.factory),
                joinedload(FactoryCustomerReference.customer),
                joinedload(FactoryCustomerReference.address),
            )
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_by_id_with_relations(
        self,
        reference_id: UUID,
    ) -> FactoryCustomerReference | None:
        stmt = (
            select(FactoryCustomerReference)
            .where(FactoryCustomerReference.id == reference_id)
            .options(
                joinedload(FactoryCustomerReference.factory),
                joinedload(FactoryCustomerReference.customer),
                joinedload(FactoryCustomerReference.address),
            )
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()
