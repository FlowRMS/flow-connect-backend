from typing import Any
from uuid import UUID

from commons.db.v6 import RbacResourceEnum, User
from commons.db.v6.commission import (
    Invoice,
    InvoiceBalance,
    InvoiceDetail,
    InvoiceSplitRate,
    Order,
)
from commons.db.v6.commission.invoices.enums import InvoiceStatus
from commons.db.v6.core import Factory
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.link_relation_model import LinkRelation
from sqlalchemy import Select, func, or_, select
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, lazyload

from app.core.context_wrapper import ContextWrapper
from app.core.exceptions import NotFoundError
from app.core.processors import ProcessorExecutor
from app.graphql.base_repository import BaseRepository
from app.graphql.invoices.processors.update_order_on_invoice_processor import (
    UpdateOrderOnInvoiceProcessor,
)
from app.graphql.invoices.processors.validate_invoice_split_rate_processor import (
    ValidateInvoiceSplitRateProcessor,
)
from app.graphql.invoices.processors.validate_invoice_status_processor import (
    ValidateInvoiceStatusProcessor,
)
from app.graphql.invoices.repositories.invoice_balance_repository import (
    InvoiceBalanceRepository,
)
from app.graphql.invoices.strawberry.invoice_landing_page_response import (
    InvoiceLandingPageResponse,
)


class InvoicesRepository(BaseRepository[Invoice]):
    entity_type = EntityType.INVOICE
    landing_model = InvoiceLandingPageResponse
    rbac_resource: RbacResourceEnum | None = RbacResourceEnum.INVOICE

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
        balance_repository: InvoiceBalanceRepository,
        processor_executor: ProcessorExecutor,
        validate_status_processor: ValidateInvoiceStatusProcessor,
        validate_split_rate_processor: ValidateInvoiceSplitRateProcessor,
        update_order_processor: UpdateOrderOnInvoiceProcessor,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            Invoice,
            processor_executor=processor_executor,
            processor_executor_classes=[
                validate_status_processor,
                validate_split_rate_processor,
                update_order_processor,
            ],
        )
        self.balance_repository = balance_repository

    def paginated_stmt(self) -> Select[Any]:
        return (
            select(
                Invoice.id,
                Invoice.created_at,
                User.full_name.label("created_by"),
                Invoice.invoice_number,
                Invoice.status,
                Invoice.entity_date,
                Invoice.due_date,
                InvoiceBalance.total.label("total"),
                Invoice.published,
                Invoice.locked,
                Order.order_number,
                Order.id.label("order_id"),
                Factory.title.label("factory_name"),
                array([Invoice.created_by_id]).label("user_ids"),
            )
            .select_from(Invoice)
            .options(lazyload("*"))
            .join(User, User.id == Invoice.created_by_id)
            .join(Order, Order.id == Invoice.order_id)
            .join(InvoiceBalance, InvoiceBalance.id == Invoice.balance_id)
            .join(Factory, Factory.id == Invoice.factory_id)
        )

    async def find_invoice_by_id(self, invoice_id: UUID) -> Invoice:
        invoice = await self.get_by_id(
            invoice_id,
            options=[
                joinedload(Invoice.details),
                joinedload(Invoice.details).joinedload(InvoiceDetail.product),
                joinedload(Invoice.details).joinedload(InvoiceDetail.uom),
                joinedload(Invoice.details).joinedload(
                    InvoiceDetail.outside_split_rates
                ),
                joinedload(Invoice.details)
                .joinedload(InvoiceDetail.outside_split_rates)
                .joinedload(InvoiceSplitRate.user),
                joinedload(Invoice.balance),
                joinedload(Invoice.order),
                joinedload(Invoice.factory),
                joinedload(Invoice.created_by),
                lazyload("*"),
            ],
        )
        if not invoice:
            raise NotFoundError(str(invoice_id))
        return invoice

    async def create_with_balance(self, invoice: Invoice) -> Invoice:
        balance = await self.balance_repository.create_from_details(invoice.details)
        invoice.balance_id = balance.id
        _ = await self.create(invoice)
        return await self.find_invoice_by_id(invoice.id)

    async def update_with_balance(self, invoice: Invoice) -> Invoice:
        updated = await self.update(invoice)
        _ = await self.balance_repository.recalculate_balance(
            updated.balance_id, updated.details
        )
        await self.session.flush()
        return await self.find_invoice_by_id(updated.id)

    async def invoice_number_exists(self, order_id: UUID, invoice_number: str) -> bool:
        result = await self.session.execute(
            select(func.count())
            .select_from(Invoice)
            .options(lazyload("*"))
            .where(
                Invoice.order_id == order_id,
                Invoice.invoice_number == invoice_number,
            )
        )
        return result.scalar_one() > 0

    async def search_by_invoice_number(
        self,
        search_term: str,
        limit: int = 20,
        *,
        open_only: bool = False,
        unlocked_only: bool = False,
    ) -> list[Invoice]:
        stmt = (
            select(Invoice)
            .options(lazyload("*"))
            .where(Invoice.invoice_number.ilike(f"%{search_term}%"))
        )
        if open_only:
            stmt = stmt.where(Invoice.status == InvoiceStatus.OPEN)
        if unlocked_only:
            stmt = stmt.where(Invoice.locked.is_(False))
        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_job_id(self, job_id: UUID) -> list[Invoice]:
        stmt = (
            select(Invoice)
            .options(lazyload("*"))
            .join(
                LinkRelation,
                or_(
                    (
                        (LinkRelation.source_entity_type == EntityType.INVOICE)
                        & (LinkRelation.target_entity_type == EntityType.JOB)
                        & (LinkRelation.target_entity_id == job_id)
                        & (LinkRelation.source_entity_id == Invoice.id)
                    ),
                    (
                        (LinkRelation.source_entity_type == EntityType.JOB)
                        & (LinkRelation.target_entity_type == EntityType.INVOICE)
                        & (LinkRelation.source_entity_id == job_id)
                        & (LinkRelation.target_entity_id == Invoice.id)
                    ),
                ),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
