from datetime import date
from decimal import Decimal
from typing import override
from uuid import UUID

from commons.db.v6 import AutoNumberEntityType
from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.db.v6.commission import Invoice, Order
from commons.dtos.common.dto_loader_service import DTOLoaderService
from commons.dtos.invoice.invoice_detail_dto import InvoiceDetailDTO
from commons.dtos.invoice.invoice_dto import InvoiceDTO
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.auto_numbers.services.auto_number_settings_service import (
    AutoNumberSettingsService,
)
from app.graphql.invoices.services.invoice_service import InvoiceService
from app.graphql.invoices.services.order_detail_matcher import OrderDetailMatcherService
from app.graphql.invoices.strawberry.invoice_detail_input import InvoiceDetailInput
from app.graphql.invoices.strawberry.invoice_input import InvoiceInput
from app.graphql.orders.repositories.orders_repository import OrdersRepository

from .base import BaseEntityConverter, ConversionResult
from .entity_mapping import EntityMapping
from .exceptions import FactoryRequiredError, OrderRequiredError


class InvoiceConverter(BaseEntityConverter[InvoiceDTO, InvoiceInput, Invoice]):
    entity_type = DocumentEntityType.INVOICES
    dto_class = InvoiceDTO

    def __init__(
        self,
        session: AsyncSession,
        dto_loader_service: DTOLoaderService,
        invoice_service: InvoiceService,
        orders_repository: OrdersRepository,
        order_detail_matcher: OrderDetailMatcherService,
        auto_number_settings_service: AutoNumberSettingsService,
    ) -> None:
        super().__init__(session, dto_loader_service)
        self.invoice_service = invoice_service
        self.orders_repository = orders_repository
        self.order_detail_matcher = order_detail_matcher
        self.auto_number_settings_service = auto_number_settings_service

    @override
    async def create_entity(self, input_data: InvoiceInput) -> Invoice:
        return await self.invoice_service.create_invoice(input_data)

    @override
    async def to_input(
        self,
        dto: InvoiceDTO,
        entity_mapping: EntityMapping,
    ) -> ConversionResult[InvoiceInput]:
        factory_id = entity_mapping.factory_id
        first_flow_index = dto.details[0].flow_detail_index if dto.details else 0
        order_id = entity_mapping.get_order_id(first_flow_index)

        if not factory_id:
            return ConversionResult.fail(FactoryRequiredError())
        if not order_id:
            return ConversionResult.fail(OrderRequiredError())

        order = await self.orders_repository.find_order_by_id(order_id)

        default_commission_rate = await self.get_factory_commission_rate(factory_id)
        default_commission_discount = await self.get_factory_commission_discount_rate(
            factory_id
        )
        default_discount_rate = await self.get_factory_discount_rate(factory_id)

        invoice_number = dto.invoice_number
        if self.auto_number_settings_service.needs_generation(invoice_number):
            invoice_number = await self.auto_number_settings_service.generate_number(
                AutoNumberEntityType.INVOICE
            )
        assert invoice_number is not None
        entity_date = dto.invoice_date or date.today()

        details = [
            await self._convert_detail(
                detail=detail,
                order=order,
                entity_mapping=entity_mapping,
                default_commission_rate=default_commission_rate,
                default_commission_discount=default_commission_discount,
                default_discount_rate=default_discount_rate,
            )
            for detail in dto.details
            if detail.flow_detail_index not in entity_mapping.skipped_product_indices
        ]

        return ConversionResult.ok(
            InvoiceInput(
                invoice_number=invoice_number,
                entity_date=entity_date,
                order_id=order_id,
                factory_id=factory_id,
                details=details,
            )
        )

    async def _convert_detail(
        self,
        detail: InvoiceDetailDTO,
        order: Order,
        entity_mapping: EntityMapping,
        default_commission_rate: Decimal,
        default_commission_discount: Decimal,
        default_discount_rate: Decimal,
    ) -> InvoiceDetailInput:
        flow_detail_index = detail.flow_detail_index
        product_id = entity_mapping.get_product_id(flow_detail_index)
        end_user_id = entity_mapping.get_end_user_id(flow_detail_index)

        quantity = Decimal(str(detail.quantity_shipped or detail.quantity or 1))
        unit_price = detail.unit_price or Decimal("0")
        item_number = detail.item_number or 1

        order_detail_id = await self._match_order_detail(
            order=order,
            unit_price=unit_price,
            part_number=detail.factory_part_number or detail.customer_part_number,
            quantity=quantity,
            item_number=item_number,
        )

        commission_rate = (
            detail.commission_rate
            if detail.commission_rate is not None
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

        return InvoiceDetailInput(
            item_number=item_number,
            quantity=quantity,
            unit_price=unit_price,
            order_detail_id=order_detail_id,
            end_user_id=end_user_id,
            product_id=product_id,
            product_name_adhoc=self._get_adhoc_name(detail) if not product_id else None,
            product_description_adhoc=detail.description if not product_id else None,
            lead_time=detail.lead_time,
            discount_rate=discount_rate,
            commission_rate=commission_rate,
            commission_discount_rate=commission_discount_rate,
        )

    async def _match_order_detail(
        self,
        order: Order,
        unit_price: Decimal,
        part_number: str | None,
        quantity: Decimal,
        item_number: int,
    ) -> UUID | None:
        return await self.order_detail_matcher.match_order_detail(
            order=order,
            unit_price=unit_price,
            part_number=part_number,
            quantity=quantity,
            item_number=item_number,
        )

    def _get_adhoc_name(self, detail: InvoiceDetailDTO) -> str | None:
        if detail.factory_part_number:
            return detail.factory_part_number
        if detail.customer_part_number:
            return detail.customer_part_number
        if detail.description:
            return detail.description[:100]
        return None

