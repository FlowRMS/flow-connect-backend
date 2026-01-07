from datetime import date
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.commission import Invoice
from commons.db.v6.commission.invoices.enums import InvoiceStatus
from commons.db.v6.crm.links.entity_type import EntityType

from app.errors.common_errors import NameAlreadyExistsError, NotFoundError
from app.graphql.invoices.factories.invoice_factory import InvoiceFactory
from app.graphql.invoices.repositories.invoices_repository import InvoicesRepository
from app.graphql.invoices.strawberry.invoice_input import InvoiceInput
from app.graphql.orders.repositories.orders_repository import OrdersRepository


class InvoiceService:
    def __init__(
        self,
        repository: InvoicesRepository,
        orders_repository: OrdersRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.orders_repository = orders_repository
        self.auth_info = auth_info

    async def find_invoice_by_id(self, invoice_id: UUID) -> Invoice:
        return await self.repository.find_invoice_by_id(invoice_id)

    async def create_invoice(self, invoice_input: InvoiceInput) -> Invoice:
        if await self.repository.invoice_number_exists(
            invoice_input.order_id, invoice_input.invoice_number
        ):
            raise NameAlreadyExistsError(invoice_input.invoice_number)

        invoice = invoice_input.to_orm_model()
        invoice.status = InvoiceStatus.OPEN
        invoice.locked = False
        return await self.repository.create_with_balance(invoice)

    async def update_invoice(self, invoice_input: InvoiceInput) -> Invoice:
        if invoice_input.id is None:
            raise ValueError("ID must be provided for update")

        invoice = invoice_input.to_orm_model()
        invoice.id = invoice_input.id
        return await self.repository.update_with_balance(invoice)

    async def delete_invoice(self, invoice_id: UUID) -> bool:
        if not await self.repository.exists(invoice_id):
            raise NotFoundError(str(invoice_id))
        return await self.repository.delete(invoice_id)

    async def search_invoices(
        self,
        search_term: str,
        limit: int = 20,
        *,
        open_only: bool = False,
        unlocked_only: bool = False,
    ) -> list[Invoice]:
        return await self.repository.search_by_invoice_number(
            search_term, limit, open_only=open_only, unlocked_only=unlocked_only
        )

    async def find_invoices_by_job_id(self, job_id: UUID) -> list[Invoice]:
        return await self.repository.find_by_job_id(job_id)

    async def find_by_entity(
        self, entity_type: EntityType, entity_id: UUID
    ) -> list[Invoice]:
        return await self.repository.find_by_entity(entity_type, entity_id)

    async def search_open_invoices(
        self,
        factory_id: UUID,
        start_from: date,
    ) -> list[Invoice]:
        return await self.repository.search_open_invoices(factory_id, start_from)

    async def find_invoices_by_order_id(self, order_id: UUID) -> list[Invoice]:
        return await self.repository.find_by_order_id(order_id)

    async def create_invoice_from_order(
        self,
        order_id: UUID,
        invoice_number: str,
        factory_id: UUID,
        order_detail_ids: list[UUID] | None = None,
        due_date: date | None = None,
    ) -> Invoice:
        order = await self.orders_repository.find_order_by_id(order_id)

        if await self.repository.invoice_number_exists(order_id, invoice_number):
            raise NameAlreadyExistsError(invoice_number)

        invoice = InvoiceFactory.from_order(
            order=order,
            invoice_number=invoice_number,
            factory_id=factory_id,
            order_detail_ids=order_detail_ids,
            due_date=due_date,
        )
        invoice.status = InvoiceStatus.OPEN
        return await self.repository.create_with_balance(invoice)
