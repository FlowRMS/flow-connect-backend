from datetime import date, datetime, timezone
from decimal import Decimal
from typing import override

from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.db.v6.models import Order
from commons.dtos.common.dto_loader_service import DTOLoaderService
from commons.dtos.order.order_detail_dto import OrderDetailDTO
from commons.dtos.order.order_dto import OrderDTO
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.orders.services.order_service import OrderService
from app.graphql.orders.strawberry.order_detail_input import OrderDetailInput
from app.graphql.orders.strawberry.order_input import OrderInput

from .base import BaseEntityConverter
from .entity_mapping import EntityMapping


class OrderConverter(BaseEntityConverter[OrderDTO, OrderInput, Order]):
    entity_type = DocumentEntityType.ORDERS
    dto_class = OrderDTO

    def __init__(
        self,
        session: AsyncSession,
        dto_loader_service: DTOLoaderService,
        order_service: OrderService,
    ) -> None:
        super().__init__(session, dto_loader_service)
        self.order_service = order_service

    @override
    async def create_entity(
        self,
        input_data: OrderInput,
    ) -> Order:
        return await self.order_service.create_order(input_data)

    @override
    async def to_input(
        self,
        dto: OrderDTO,
        entity_mapping: EntityMapping,
    ) -> OrderInput:
        factory_id = entity_mapping.factory_id
        sold_to_id = entity_mapping.sold_to_customer_id

        if not factory_id:
            raise ValueError("Factory ID is required but not found in entity_mapping")
        if not sold_to_id:
            raise ValueError(
                "Sold-to customer ID is required but not found in entity_mapping"
            )

        default_commission_rate = await self.get_factory_commission_rate(factory_id)
        default_commission_discount = await self.get_factory_commission_discount_rate(
            factory_id
        )
        default_discount_rate = await self.get_factory_discount_rate(factory_id)

        order_number = dto.order_number or self._generate_order_number()
        entity_date = dto.order_date or date.today()
        due_date = dto.due_date or entity_date

        details = [
            self._convert_detail(
                detail=detail,
                entity_mapping=entity_mapping,
                default_commission_rate=default_commission_rate,
                default_commission_discount=default_commission_discount,
                default_discount_rate=default_discount_rate,
            )
            for detail in dto.details
        ]

        return OrderInput(
            order_number=f"{order_number}-TEST-2",
            entity_date=entity_date,
            due_date=due_date,
            sold_to_customer_id=sold_to_id,
            factory_id=factory_id,
            bill_to_customer_id=entity_mapping.bill_to_customer_id,
            shipping_terms=dto.shipping_terms,
            ship_date=dto.ship_date,
            mark_number=dto.mark_number,
            details=details,
        )

    def _convert_detail(
        self,
        detail: OrderDetailDTO,
        entity_mapping: EntityMapping,
        default_commission_rate: Decimal,
        default_commission_discount: Decimal,
        default_discount_rate: Decimal,
    ) -> OrderDetailInput:
        flow_index = detail.flow_index
        product_id = entity_mapping.get_product_id(flow_index)
        end_user_id = entity_mapping.get_end_user_id(flow_index)

        if not end_user_id:
            raise ValueError(
                f"End user ID is required for detail at index {flow_index}"
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

        return OrderDetailInput(
            item_number=detail.item_number or 1,
            quantity=Decimal(str(detail.quantity or 1)),
            unit_price=detail.unit_price or Decimal("0"),
            end_user_id=end_user_id,
            product_id=product_id,
            product_name_adhoc=self._get_adhoc_name(detail) if not product_id else None,
            product_description_adhoc=detail.description if not product_id else None,
            lead_time=detail.lead_time,
            discount_rate=discount_rate,
            commission_rate=commission_rate,
            commission_discount_rate=commission_discount_rate,
        )

    def _get_adhoc_name(self, detail: OrderDetailDTO) -> str | None:
        if detail.factory_part_number:
            return detail.factory_part_number
        if detail.customer_part_number:
            return detail.customer_part_number
        if detail.description:
            return detail.description[:100]
        return None

    @staticmethod
    def _generate_order_number() -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"ORD-{timestamp}"
