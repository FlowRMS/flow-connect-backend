from datetime import date, datetime, timezone
from decimal import Decimal
from typing import override
from uuid import UUID

from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.db.v6.commission import Order, OrderAcknowledgement
from commons.dtos.common.dto_loader_service import DTOLoaderService
from commons.dtos.order.order_ack_dto import OrderAckDTO
from commons.dtos.order.order_detail_dto import OrderDetailDTO
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.invoices.services.order_detail_matcher import OrderDetailMatcherService
from app.graphql.orders.repositories.orders_repository import OrdersRepository
from app.graphql.orders.services.order_acknowledgement_service import (
    OrderAcknowledgementService,
)
from app.graphql.orders.strawberry.order_acknowledgement_input import (
    OrderAcknowledgementInput,
)

from .base import BaseEntityConverter, ConversionResult
from .entity_mapping import EntityMapping
from .exceptions import FactoryRequiredError, OrderRequiredError


class OrderAckConverter(
    BaseEntityConverter[OrderAckDTO, OrderAcknowledgementInput, OrderAcknowledgement]
):
    entity_type = DocumentEntityType.ORDER_ACKNOWLEDGEMENTS
    dto_class = OrderAckDTO

    def __init__(
        self,
        session: AsyncSession,
        dto_loader_service: DTOLoaderService,
        order_ack_service: OrderAcknowledgementService,
        orders_repository: OrdersRepository,
        order_detail_matcher: OrderDetailMatcherService,
    ) -> None:
        super().__init__(session, dto_loader_service)
        self.order_ack_service = order_ack_service
        self.orders_repository = orders_repository
        self.order_detail_matcher = order_detail_matcher

    @override
    async def find_existing(
        self, input_data: OrderAcknowledgementInput
    ) -> OrderAcknowledgement | None:
        existing = await self.order_ack_service.find_by_order_detail_id(
            input_data.order_detail_id
        )
        for ack in existing:
            if (
                ack.order_acknowledgement_number
                == input_data.order_acknowledgement_number
            ):
                return ack
        return None

    @override
    async def create_entity(
        self,
        input_data: OrderAcknowledgementInput,
    ) -> OrderAcknowledgement:
        existing = await self.find_existing(input_data)
        if existing:
            return existing
        return await self.order_ack_service.create(input_data)

    @override
    async def to_input(
        self,
        dto: OrderAckDTO,
        entity_mapping: EntityMapping,
    ) -> ConversionResult[OrderAcknowledgementInput]:
        factory_id = entity_mapping.factory_id
        first_flow_index = dto.details[0].flow_detail_index if dto.details else 0
        order_id = entity_mapping.get_order_id(first_flow_index)

        if not factory_id:
            return ConversionResult.fail(FactoryRequiredError())
        if not order_id:
            return ConversionResult.fail(OrderRequiredError())

        order = await self.orders_repository.find_order_by_id(order_id)
        if not order:
            return ConversionResult.fail(OrderRequiredError())

        first_detail = dto.details[0] if dto.details else None
        if not first_detail:
            return ConversionResult.fail(OrderRequiredError())

        order_detail_id = await self._match_order_detail(
            order=order,
            detail=first_detail,
        )
        if not order_detail_id:
            return ConversionResult.fail(OrderRequiredError())

        ack_number = dto.ack_number or self._generate_ack_number()
        entity_date = dto.ack_date or date.today()
        quantity = Decimal(str(first_detail.quantity or 1))

        return ConversionResult.ok(
            OrderAcknowledgementInput(
                order_id=order_id,
                order_detail_id=order_detail_id,
                order_acknowledgement_number=ack_number,
                entity_date=entity_date,
                quantity=quantity,
            )
        )

    async def _match_order_detail(
        self,
        order: Order,
        detail: OrderDetailDTO,
    ) -> UUID | None:
        unit_price = detail.unit_price or Decimal("0")
        quantity = Decimal(str(detail.quantity or 1))
        item_number = detail.item_number or 1

        return await self.order_detail_matcher.match_order_detail(
            order=order,
            unit_price=unit_price,
            part_number=detail.factory_part_number or detail.customer_part_number,
            quantity=quantity,
            item_number=item_number,
        )

    @staticmethod
    def _generate_ack_number() -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"ACK-{timestamp}"
