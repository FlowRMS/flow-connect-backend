from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from commons.db.v6.ai.documents.enums import EntityType
from commons.dtos.order.order_detail_dto import OrderDetailDTO
from commons.dtos.order.order_dto import OrderDTO

from app.graphql.orders.strawberry.order_detail_input import OrderDetailInput
from app.graphql.orders.strawberry.order_input import OrderInput

from .base import BaseEntityConverter
from .registry import register_converter


@register_converter(EntityType.ORDERS)
class OrderConverter(BaseEntityConverter[OrderDTO, OrderInput]):
    def to_input(
        self,
        dto: OrderDTO,
        entity_mapping: dict[str, UUID],
    ) -> OrderInput:
        factory_id = entity_mapping.get("factory")
        sold_to_id = entity_mapping.get("sold_to_customer")

        if not factory_id:
            raise ValueError("Factory ID is required but not found in entity_mapping")
        if not sold_to_id:
            raise ValueError(
                "Sold-to customer ID is required but not found in entity_mapping"
            )

        order_number = dto.order_number or self._generate_order_number()
        entity_date = dto.order_date or date.today()
        due_date = dto.due_date or entity_date

        details = [
            self._convert_detail(detail, entity_mapping, sold_to_id)
            for detail in dto.details
        ]

        return OrderInput(
            order_number=order_number,
            entity_date=entity_date,
            due_date=due_date,
            sold_to_customer_id=sold_to_id,
            factory_id=factory_id,
            bill_to_customer_id=entity_mapping.get("bill_to_customer"),
            shipping_terms=dto.shipping_terms,
            ship_date=dto.ship_date,
            mark_number=dto.mark_number,
            details=details,
        )

    def _convert_detail(
        self,
        dto_detail: OrderDetailDTO,
        entity_mapping: dict[str, UUID],
        fallback_end_user_id: UUID,
    ) -> OrderDetailInput:
        flow_index = dto_detail.flow_index
        product_key = f"product_{flow_index}" if flow_index is not None else None
        end_user_key = f"end_user_{flow_index}" if flow_index is not None else None

        product_id = entity_mapping.get(product_key) if product_key else None
        end_user_id = entity_mapping.get(end_user_key) if end_user_key else None

        if not end_user_id:
            end_user_id = fallback_end_user_id

        return OrderDetailInput(
            item_number=dto_detail.item_number or 1,
            quantity=Decimal(str(dto_detail.quantity or 1)),
            unit_price=dto_detail.unit_price or Decimal("0"),
            end_user_id=end_user_id,
            product_id=product_id,
            product_name_adhoc=self._get_adhoc_name(dto_detail)
            if not product_id
            else None,
            product_description_adhoc=dto_detail.description
            if not product_id
            else None,
            lead_time=dto_detail.lead_time,
            discount_rate=dto_detail.discount_rate or Decimal("0"),
            commission_rate=dto_detail.commission_rate or Decimal("0"),
            commission_discount_rate=dto_detail.commission_discount_rate
            or Decimal("0"),
        )

    def _get_adhoc_name(self, dto_detail: OrderDetailDTO) -> str | None:
        if dto_detail.factory_part_number:
            return dto_detail.factory_part_number
        if dto_detail.customer_part_number:
            return dto_detail.customer_part_number
        if dto_detail.description:
            return dto_detail.description[:100]
        return None

    @staticmethod
    def _generate_order_number() -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"AUTO-{timestamp}"
