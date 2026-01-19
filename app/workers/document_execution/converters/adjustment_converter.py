from datetime import date, datetime, timezone
from decimal import Decimal
from typing import override
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.commission import Adjustment
from commons.db.v6.commission.checks.enums import AdjustmentAllocationMethod
from commons.db.v6.common.creation_type import CreationType
from commons.dtos.check.check_detail_dto import CheckDetailDTO
from commons.dtos.common.dto_loader_service import DTOLoaderService
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.adjustments.services.adjustment_service import AdjustmentService
from app.graphql.adjustments.strawberry.adjustment_input import AdjustmentInput
from app.graphql.adjustments.strawberry.adjustment_split_rate_input import (
    AdjustmentSplitRateInput,
)

from .base import BaseEntityConverter, ConversionResult
from .entity_mapping import EntityMapping
from .exceptions import FactoryRequiredError


class AdjustmentConverter(
    BaseEntityConverter[CheckDetailDTO, AdjustmentInput, Adjustment]
):
    dto_class = CheckDetailDTO

    def __init__(
        self,
        auth_info: AuthInfo,
        session: AsyncSession,
        dto_loader_service: DTOLoaderService,
        adjustment_service: AdjustmentService,
    ) -> None:
        super().__init__(session, dto_loader_service)
        self.auth_info = auth_info
        self.adjustment_service = adjustment_service

    @override
    async def find_existing(self, input_data: AdjustmentInput) -> Adjustment | None:
        return await self.adjustment_service.find_by_adjustment_number(
            input_data.factory_id,
            input_data.adjustment_number,
        )

    @override
    async def create_entity(
        self,
        input_data: AdjustmentInput,
    ) -> Adjustment:
        existing = await self.find_existing(input_data)
        if existing:
            return existing
        return await self.adjustment_service.create_adjustment(input_data)

    @override
    async def to_input(
        self,
        dto: CheckDetailDTO,
        entity_mapping: EntityMapping,
    ) -> ConversionResult[AdjustmentInput]:
        factory_id = entity_mapping.factory_id

        if not factory_id:
            return ConversionResult.fail(FactoryRequiredError())

        adjustment_number = dto.invoice_number or self._generate_adjustment_number()
        entity_date = dto.invoice_date or date.today()
        amount = dto.paid_commission_amount or Decimal("0")

        customer_id = entity_mapping.sold_to_customer_id
        allocation_method = self._determine_allocation_method(customer_id)

        split_rates = self._build_split_rates()

        return ConversionResult.ok(
            AdjustmentInput(
                adjustment_number=adjustment_number,
                entity_date=entity_date,
                factory_id=factory_id,
                amount=amount,
                allocation_method=allocation_method,
                split_rates=split_rates,
                customer_id=customer_id,
                reason=dto.description,
                creation_type=CreationType.API,
            )
        )

    def _determine_allocation_method(
        self,
        customer_id: UUID | None,
    ) -> AdjustmentAllocationMethod:
        if customer_id:
            return AdjustmentAllocationMethod.CUSTOMER
        return AdjustmentAllocationMethod.REP_SPLIT

    def _build_split_rates(self) -> list[AdjustmentSplitRateInput]:
        return [
            AdjustmentSplitRateInput(
                user_id=self.auth_info.flow_user_id,
                split_rate=Decimal("100"),
                position=1,
            )
        ]

    @staticmethod
    def _generate_adjustment_number() -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"ADJ-{timestamp}"
