from datetime import date, datetime, timezone
from decimal import Decimal
from typing import override
from uuid import UUID

from commons.db.v6.commission import Credit, Order
from commons.db.v6.commission.credits.enums import CreditType
from commons.db.v6.common.creation_type import CreationType
from commons.dtos.check.check_detail_dto import CheckDetailDTO
from commons.dtos.common.dto_loader_service import DTOLoaderService
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.credits.services.credit_service import CreditService
from app.graphql.credits.strawberry.credit_detail_input import CreditDetailInput
from app.graphql.credits.strawberry.credit_input import CreditInput
from app.graphql.invoices.services.order_detail_matcher import OrderDetailMatcherService
from app.graphql.orders.repositories.orders_repository import OrdersRepository

from .base import BaseEntityConverter, ConversionResult
from .entity_mapping import EntityMapping
from .exceptions import OrderRequiredError


class CreditConverter(BaseEntityConverter[CheckDetailDTO, CreditInput, Credit]):
    dto_class = CheckDetailDTO

    def __init__(
        self,
        session: AsyncSession,
        dto_loader_service: DTOLoaderService,
        credit_service: CreditService,
        orders_repository: OrdersRepository,
        order_detail_matcher: OrderDetailMatcherService,
    ) -> None:
        super().__init__(session, dto_loader_service)
        self.credit_service = credit_service
        self.orders_repository = orders_repository
        self.order_detail_matcher = order_detail_matcher

    @override
    async def create_entity(self, input_data: CreditInput) -> Credit:
        return await self.credit_service.create_credit(input_data)

    @override
    async def to_input(
        self,
        dto: CheckDetailDTO,
        entity_mapping: EntityMapping,
    ) -> ConversionResult[CreditInput]:
        order_id = entity_mapping.order_id

        if not order_id:
            return ConversionResult.fail(OrderRequiredError())

        order = await self.orders_repository.find_order_by_id(order_id)
        if not order:
            logger.warning(f"Order {order_id} not found for credit conversion")
            return ConversionResult.fail(OrderRequiredError())

        credit_number = dto.invoice_number or self._generate_credit_number()
        entity_date = dto.invoice_date or date.today()
        amount = abs(dto.paid_commission_amount or Decimal("0"))

        default_commission_rate = (
            await self.get_factory_commission_rate(entity_mapping.factory_id)
            if entity_mapping.factory_id
            else Decimal("0")
        )

        detail = await self._convert_detail(
            detail=dto,
            order=order,
            entity_mapping=entity_mapping,
            default_commission_rate=default_commission_rate,
            amount=amount,
        )

        return ConversionResult.ok(
            CreditInput(
                credit_number=credit_number,
                entity_date=entity_date,
                order_id=order_id,
                credit_type=CreditType.OTHER,
                details=[detail],
                reason=dto.description,
                creation_type=CreationType.API,
            )
        )

    async def _convert_detail(
        self,
        detail: CheckDetailDTO,
        order: Order,
        entity_mapping: EntityMapping,
        default_commission_rate: Decimal,
        amount: Decimal,
    ) -> CreditDetailInput:
        quantity = Decimal(str(detail.quantity_shipped or 1))
        unit_price = amount / quantity if quantity else amount
        item_number = detail.item_number or 1

        order_detail_id = await self._match_order_detail(
            order=order,
            unit_price=unit_price,
            part_number=detail.factory_part_number or detail.customer_part_number,
            quantity=quantity,
            item_number=item_number,
        )

        if not order_detail_id and order.details:
            order_detail_id = order.details[0].id
            logger.warning(
                f"Could not match order detail for credit, using first detail: {order_detail_id}"
            )

        if not order_detail_id:
            raise ValueError("No order details available for credit")

        commission_rate = (
            detail.commission_discount_rate
            if detail.commission_discount_rate is not None
            else default_commission_rate
        )

        return CreditDetailInput(
            item_number=item_number,
            quantity=quantity,
            unit_price=unit_price,
            commission_rate=commission_rate,
            order_detail_id=order_detail_id,
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

    @staticmethod
    def _generate_credit_number() -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"CRD-{timestamp}"
