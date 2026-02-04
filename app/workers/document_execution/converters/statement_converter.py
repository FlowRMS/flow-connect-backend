from datetime import date
from decimal import Decimal
from typing import override
from uuid import UUID

from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.db.v6.commission import Invoice, Order
from commons.db.v6.commission.statements import CommissionStatement
from commons.dtos.common.dto_loader_service import DTOLoaderService
from commons.dtos.statement.statement_detail_dto import CommissionStatementDetailDTO
from commons.dtos.statement.statement_dto import CommissionStatementDTO
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.graphql.invoices.services.order_detail_matcher import OrderDetailMatcherService
from app.graphql.orders.repositories.orders_repository import OrdersRepository
from app.graphql.statements.services.statement_service import StatementService
from app.graphql.statements.strawberry.statement_detail_input import (
    StatementDetailInput,
)
from app.graphql.statements.strawberry.statement_input import StatementInput

from .base import BaseEntityConverter, ConversionResult
from .entity_mapping import EntityMapping
from .exceptions import FactoryRequiredError


DEFAULT_QUANTITY = Decimal("1")

class StatementConverter(
    BaseEntityConverter[CommissionStatementDTO, StatementInput, CommissionStatement]
):
    entity_type = DocumentEntityType.COMMISSION_STATEMENTS
    dto_class = CommissionStatementDTO

    def __init__(
        self,
        session: AsyncSession,
        dto_loader_service: DTOLoaderService,
        statement_service: StatementService,
        orders_repository: OrdersRepository,
        order_detail_matcher: OrderDetailMatcherService,
    ) -> None:
        super().__init__(session, dto_loader_service)
        self.statement_service = statement_service
        self.orders_repository = orders_repository
        self.order_detail_matcher = order_detail_matcher
        self._invoice_cache: dict[tuple[str, UUID], Invoice | None] = {}
        self._order_cache: dict[UUID, Order | None] = {}

    @override
    async def find_existing(
        self, input_data: StatementInput
    ) -> CommissionStatement | None:
        return await self.statement_service.find_by_statement_number(
            input_data.factory_id,
            input_data.statement_number,
        )

    @override
    async def create_entity(self, input_data: StatementInput) -> CommissionStatement:
        existing = await self.find_existing(input_data)
        if existing:
            return existing
        return await self.statement_service.create_statement(input_data)

    @override
    async def to_input(
        self,
        dto: CommissionStatementDTO,
        entity_mapping: EntityMapping,
    ) -> ConversionResult[StatementInput]:
        factory_id = entity_mapping.factory_id

        if not factory_id:
            return ConversionResult.fail(FactoryRequiredError())

        statement_number = (
            dto.commission_number or f"S-{date.today().strftime('%Y%m%d')}-GEN"
        )
        entity_date = dto.entity_date or date.today()

        default_commission_rate = await self.get_factory_commission_rate(factory_id)
        default_commission_discount = await self.get_factory_commission_discount_rate(
            factory_id
        )
        default_discount_rate = await self.get_factory_discount_rate(factory_id)

        details: list[StatementDetailInput] = []
        for idx, detail in enumerate(dto.details):
            if detail.flow_detail_index in entity_mapping.skipped_product_indices:
                continue
            detail_input = await self._convert_detail(
                detail=detail,
                item_number=idx + 1,
                entity_mapping=entity_mapping,
                default_commission_rate=default_commission_rate,
                default_commission_discount=default_commission_discount,
                default_discount_rate=default_discount_rate,
            )
            details.append(detail_input)

        return ConversionResult.ok(
            StatementInput(
                statement_number=statement_number,
                entity_date=entity_date,
                factory_id=factory_id,
                details=details,
            )
        )

    async def _convert_detail(
        self,
        detail: CommissionStatementDetailDTO,
        item_number: int,
        entity_mapping: EntityMapping,
        default_commission_rate: Decimal,
        default_commission_discount: Decimal,
        default_discount_rate: Decimal,
    ) -> StatementDetailInput:
        flow_detail_index = detail.flow_detail_index
        product_id = entity_mapping.get_product_id(flow_detail_index)
        end_user_id = entity_mapping.get_end_user_id(flow_detail_index)
        order_id = entity_mapping.get_order_id(flow_detail_index)
        invoice_id = entity_mapping.get_invoice_id(flow_detail_index)

        quantity = (
            Decimal(str(detail.quantity_determined))
            if detail.quantity_determined
            else DEFAULT_QUANTITY
        )
        unit_price = (
            detail.unit_price_determined
            if detail.unit_price_determined is not None
            else Decimal("0")
        )

        order_detail_id = await self._match_order_detail(
            order_id=order_id,
            unit_price=unit_price,
            part_number=detail.factory_part_number or detail.customer_part_number,
            quantity=quantity,
            item_number=item_number,
        )

        commission_rate = (
            detail.commission_rate_determined
            if detail.commission_rate_determined is not None
            else default_commission_rate
        )
        commission_discount_rate = (
            detail.commission_discount_rate
            if detail.commission_discount_rate is not None
            else default_commission_discount
        )
        discount_rate = (
            detail.discount_rate
            if detail.discount_rate is not None
            else default_discount_rate
        )

        commission = (
            detail.total_line_commission
            if detail.total_line_commission is not None
            else detail.paid_commission_amount
        )

        sold_to_customer_id = entity_mapping.sold_to_customer_id

        return StatementDetailInput(
            item_number=item_number,
            quantity=quantity,
            unit_price=unit_price,
            sold_to_customer_id=sold_to_customer_id,
            order_id=order_id,
            order_detail_id=order_detail_id,
            invoice_id=invoice_id,
            end_user_id=end_user_id,
            product_id=product_id,
            product_name_adhoc=self._get_adhoc_name(detail) if not product_id else None,
            product_description_adhoc=detail.description if not product_id else None,
            lead_time=detail.lead_time,
            discount_rate=discount_rate,
            commission_rate=commission_rate,
            commission_discount_rate=commission_discount_rate,
            commission=commission,
        )

    async def _match_order_detail(
        self,
        order_id: UUID | None,
        unit_price: Decimal,
        part_number: str | None,
        quantity: Decimal,
        item_number: int,
    ) -> UUID | None:
        if not order_id:
            return None

        order = await self._get_order(order_id)
        if not order:
            return None

        return await self.order_detail_matcher.match_order_detail(
            order=order,
            unit_price=unit_price,
            part_number=part_number,
            quantity=quantity,
            item_number=item_number,
        )

    async def _get_order(self, order_id: UUID) -> Order | None:
        if order_id in self._order_cache:
            return self._order_cache[order_id]

        order = await self.orders_repository.find_order_by_id(order_id)
        self._order_cache[order_id] = order
        return order

    async def _find_invoice_by_number_and_factory(
        self,
        invoice_number: str,
        factory_id: UUID,
    ) -> Invoice | None:
        cache_key = (invoice_number, factory_id)
        if cache_key in self._invoice_cache:
            return self._invoice_cache[cache_key]

        stmt = (
            select(Invoice)
            .options(lazyload("*"))
            .where(
                Invoice.invoice_number == invoice_number,
                Invoice.factory_id == factory_id,
            )
        )
        result = await self.session.execute(stmt)
        invoice = result.scalar_one_or_none()

        self._invoice_cache[cache_key] = invoice
        return invoice

    def _get_adhoc_name(self, detail: CommissionStatementDetailDTO) -> str | None:
        if detail.factory_part_number:
            return detail.factory_part_number
        if detail.customer_part_number:
            return detail.customer_part_number
        if detail.description:
            return detail.description[:100]
        return None
