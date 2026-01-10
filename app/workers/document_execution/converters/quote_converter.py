from datetime import date, datetime, timezone
from decimal import Decimal
from typing import override
from uuid import UUID

from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.db.v6.crm.quotes import PipelineStage, Quote, QuoteStatus
from commons.dtos.common.dto_loader_service import DTOLoaderService
from commons.dtos.quote.quote_detail_dto import BaseQuoteDetailDTO
from commons.dtos.quote.quote_dto import QuoteDTO
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.quotes.services.quote_service import QuoteService
from app.graphql.quotes.strawberry.quote_detail_input import QuoteDetailInput
from app.graphql.quotes.strawberry.quote_input import QuoteInput

from .base import BaseEntityConverter, ConversionResult
from .entity_mapping import EntityMapping
from .exceptions import FactoryRequiredError, SoldToCustomerRequiredError


class QuoteConverter(BaseEntityConverter[QuoteDTO, QuoteInput, Quote]):
    entity_type = DocumentEntityType.QUOTES
    dto_class = QuoteDTO

    def __init__(
        self,
        session: AsyncSession,
        dto_loader_service: DTOLoaderService,
        quote_service: QuoteService,
    ) -> None:
        super().__init__(session, dto_loader_service)
        self.quote_service = quote_service

    @override
    async def create_entity(
        self,
        input_data: QuoteInput,
    ) -> Quote:
        return await self.quote_service.create_quote(input_data)

    @override
    async def to_input(
        self,
        dto: QuoteDTO,
        entity_mapping: EntityMapping,
    ) -> ConversionResult[QuoteInput]:
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

        quote_number = dto.quote_number or self._generate_quote_number()
        entity_date = dto.quote_date or date.today()

        details = [
            self._convert_detail(
                detail=detail,
                entity_mapping=entity_mapping,
                factory_id=factory_id,
                default_commission_rate=default_commission_rate,
                default_commission_discount=default_commission_discount,
                default_discount_rate=default_discount_rate,
            )
            for detail in dto.details
        ]

        return ConversionResult.ok(
            QuoteInput(
                quote_number=quote_number,
                entity_date=entity_date,
                sold_to_customer_id=sold_to_id,
                status=QuoteStatus.OPEN,
                pipeline_stage=PipelineStage.PROPOSAL,
                bill_to_customer_id=entity_mapping.bill_to_customer_id,
                payment_terms=dto.payment_terms,
                freight_terms=dto.freight_terms,
                exp_date=dto.expiration_date,
                details=details,
                published=True,
            )
        )

    def _convert_detail(
        self,
        detail: BaseQuoteDetailDTO,
        entity_mapping: EntityMapping,
        factory_id: UUID,
        default_commission_rate: Decimal,
        default_commission_discount: Decimal,
        default_discount_rate: Decimal,
    ) -> QuoteDetailInput:
        flow_index = detail.flow_index
        product_id = entity_mapping.get_product_id(flow_index)
        end_user_id = entity_mapping.get_end_user_id(flow_index)

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

        return QuoteDetailInput(
            item_number=detail.item_number or 1,
            quantity=Decimal(str(detail.quantity or 1)),
            unit_price=detail.unit_price or Decimal("0"),
            end_user_id=end_user_id,
            factory_id=factory_id,
            product_id=product_id,
            product_name_adhoc=self._get_adhoc_name(detail) if not product_id else None,
            product_description_adhoc=detail.description if not product_id else None,
            lead_time=detail.lead_time,
            discount_rate=discount_rate,
            commission_rate=commission_rate,
            commission_discount_rate=commission_discount_rate,
        )

    def _get_adhoc_name(self, detail: BaseQuoteDetailDTO) -> str | None:
        if detail.factory_part_number:
            return detail.factory_part_number
        if detail.customer_part_number:
            return detail.customer_part_number
        if detail.description:
            return detail.description[:100]
        return None

    @staticmethod
    def _generate_quote_number() -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"QTE-{timestamp}"
