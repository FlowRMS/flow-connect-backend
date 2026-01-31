from datetime import date
from decimal import Decimal
from typing import override

from commons.db.v6 import AutoNumberEntityType
from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.db.v6.models import Order
from commons.dtos.common.dto_loader_service import DTOLoaderService
from commons.dtos.order.order_detail_dto import OrderDetailDTO
from commons.dtos.order.order_dto import OrderDTO
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.auto_numbers.services.auto_number_settings_service import (
    AutoNumberSettingsService,
)
from app.graphql.orders.services.order_service import OrderService
from app.graphql.orders.strawberry.order_detail_input import OrderDetailInput
from app.graphql.orders.strawberry.order_input import OrderInput

from .base import (
    BaseEntityConverter,
    BulkCreateResult,
    ConversionResult,
    SeparatedInputs,
)
from .entity_mapping import EntityMapping
from .exceptions import (
    EndUserRequiredError,
    FactoryRequiredError,
    SoldToCustomerRequiredError,
)


class OrderConverter(BaseEntityConverter[OrderDTO, OrderInput, Order]):
    entity_type = DocumentEntityType.ORDERS
    dto_class = OrderDTO

    def __init__(
        self,
        session: AsyncSession,
        dto_loader_service: DTOLoaderService,
        order_service: OrderService,
        auto_number_settings_service: AutoNumberSettingsService,
    ) -> None:
        super().__init__(session, dto_loader_service)
        self.order_service = order_service
        self.auto_number_settings_service = auto_number_settings_service

    @override
    async def find_existing(self, input_data: OrderInput) -> Order | None:
        return await self.order_service.find_by_order_number(
            input_data.order_number,
            input_data.sold_to_customer_id,
        )

    @override
    async def create_entity(
        self,
        input_data: OrderInput,
    ) -> Order:
        existing = await self.find_existing(input_data)
        if existing:
            return existing
        return await self.order_service.create_order(input_data)

    @override
    async def separate_inputs(
        self,
        inputs: list[OrderInput],
    ) -> SeparatedInputs[OrderInput]:
        if not inputs:
            return SeparatedInputs(
                for_creation=[],
                for_creation_indices=[],
                for_update=[],
                for_update_indices=[],
            )

        pairs = [(inp.order_number, inp.sold_to_customer_id) for inp in inputs]
        existing_orders = await self.order_service.get_existing_orders(pairs)
        existing_map = {
            (o.order_number, o.sold_to_customer_id): o for o in existing_orders
        }

        for_creation: list[OrderInput] = []
        for_creation_indices: list[int] = []
        for_update: list[tuple[OrderInput, Order]] = []
        for_update_indices: list[int] = []

        for i, inp in enumerate(inputs):
            key = (inp.order_number, inp.sold_to_customer_id)
            existing = existing_map.get(key)
            if existing:
                inp.id = existing.id
                for_update.append((inp, existing))
                for_update_indices.append(i)
            else:
                for_creation.append(inp)
                for_creation_indices.append(i)

        return SeparatedInputs(
            for_creation=for_creation,
            for_creation_indices=for_creation_indices,
            for_update=for_update,
            for_update_indices=for_update_indices,
        )

    @override
    async def update_entities_bulk(
        self,
        inputs_with_entities: list[tuple[OrderInput, Order]],
    ) -> BulkCreateResult[Order]:
        if not inputs_with_entities:
            return BulkCreateResult(created=[], skipped_indices=[])

        updated: list[Order] = []
        skipped: list[int] = []
        for i, (inp, _existing) in enumerate(inputs_with_entities):
            try:
                order = await self.order_service.update_order(inp)
                updated.append(order)
            except Exception:
                skipped.append(i)

        return BulkCreateResult(created=updated, skipped_indices=skipped)

    @override
    async def to_input(
        self,
        dto: OrderDTO,
        entity_mapping: EntityMapping,
    ) -> ConversionResult[OrderInput]:
        factory_id = entity_mapping.factory_id
        sold_to_id = entity_mapping.sold_to_customer_id

        if not factory_id:
            return ConversionResult.fail(FactoryRequiredError())
        if not sold_to_id:
            return ConversionResult.fail(SoldToCustomerRequiredError())

        default_commission_rate = await self.get_factory_commission_rate(factory_id)
        default_commission_discount = await self.get_factory_commission_discount_rate(
            factory_id
        )
        default_discount_rate = await self.get_factory_discount_rate(factory_id)

        order_number = dto.order_number
        if self.auto_number_settings_service.needs_generation(order_number):
            order_number = await self.auto_number_settings_service.generate_number(
                AutoNumberEntityType.ORDER
            )
        entity_date = dto.order_date or date.today()
        due_date = dto.due_date or entity_date

        details: list[OrderDetailInput] = []
        for detail in dto.details:
            if detail.flow_detail_index in entity_mapping.skipped_product_indices:
                continue
            detail_result = self._convert_detail(
                detail=detail,
                entity_mapping=entity_mapping,
                default_commission_rate=default_commission_rate,
                default_commission_discount=default_commission_discount,
                default_discount_rate=default_discount_rate,
            )
            if detail_result.is_error():
                return ConversionResult.fail(detail_result.unwrap_error())
            details.append(detail_result.unwrap())

        return ConversionResult.ok(
            OrderInput(
                order_number=order_number or f"O-{date.today().strftime('%Y%m%d')}-GEN",
                entity_date=entity_date,
                due_date=due_date,
                sold_to_customer_id=sold_to_id,
                factory_id=factory_id,
                bill_to_customer_id=entity_mapping.bill_to_customer_id,
                shipping_terms=dto.shipping_terms,
                ship_date=dto.ship_date,
                mark_number=dto.mark_number,
                details=details,
                published=True,
            )
        )

    def _convert_detail(
        self,
        detail: OrderDetailDTO,
        entity_mapping: EntityMapping,
        default_commission_rate: Decimal,
        default_commission_discount: Decimal,
        default_discount_rate: Decimal,
    ) -> ConversionResult[OrderDetailInput]:
        flow_detail_index = detail.flow_detail_index
        product_id = entity_mapping.get_product_id(flow_detail_index)
        end_user_id = entity_mapping.get_end_user_id(flow_detail_index)

        if not end_user_id:
            return ConversionResult.fail(EndUserRequiredError(flow_detail_index))

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

        return ConversionResult.ok(
            OrderDetailInput(
                item_number=detail.item_number or 1,
                quantity=Decimal(str(detail.quantity or 1)),
                unit_price=detail.unit_price or Decimal("0"),
                end_user_id=end_user_id,
                product_id=product_id,
                product_name_adhoc=self._get_adhoc_name(detail)
                if not product_id
                else None,
                product_description_adhoc=detail.description
                if not product_id
                else None,
                lead_time=detail.lead_time,
                discount_rate=discount_rate,
                commission_rate=commission_rate,
                commission_discount_rate=commission_discount_rate,
            )
        )

    def _get_adhoc_name(self, detail: OrderDetailDTO) -> str | None:
        if detail.factory_part_number:
            return detail.factory_part_number
        if detail.customer_part_number:
            return detail.customer_part_number
        if detail.description:
            return detail.description[:100]
        return None

    @override
    async def create_entities_bulk(
        self,
        inputs: list[OrderInput],
    ) -> BulkCreateResult[Order]:
        if not inputs:
            return BulkCreateResult(created=[], skipped_indices=[])

        try:
            created = await self.order_service.create_orders_bulk(inputs)
            skipped_count = len(inputs) - len(created)
            skipped_indices = list(range(len(created), len(created) + skipped_count))
            return BulkCreateResult(created=created, skipped_indices=skipped_indices)
        except Exception as e:
            logger.error(f"Bulk order creation failed: {e}, falling back to sequential")
            return await super().create_entities_bulk(inputs)
