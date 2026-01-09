from datetime import date, datetime, timezone
from decimal import Decimal
from typing import override
from uuid import UUID

from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.db.v6.commission import Adjustment, Check, Credit, Invoice
from commons.dtos.check.check_detail_dto import CheckDetailDTO
from commons.dtos.check.check_dto import CheckDTO
from commons.dtos.common.dto_loader_service import DTOLoaderService
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.graphql.checks.services.check_service import CheckService
from app.graphql.checks.strawberry.check_detail_input import CheckDetailInput
from app.graphql.checks.strawberry.check_input import CheckInput

from .adjustment_converter import AdjustmentConverter
from .base import BaseEntityConverter, ConversionResult
from .credit_converter import CreditConverter
from .entity_mapping import EntityMapping
from .exceptions import FactoryRequiredError


class CheckConverter(BaseEntityConverter[CheckDTO, CheckInput, Check]):
    entity_type = DocumentEntityType.CHECKS
    dto_class = CheckDTO

    def __init__(
        self,
        session: AsyncSession,
        dto_loader_service: DTOLoaderService,
        check_service: CheckService,
        credit_converter: CreditConverter,
        adjustment_converter: AdjustmentConverter,
    ) -> None:
        super().__init__(session, dto_loader_service)
        self.check_service = check_service
        self.credit_converter = credit_converter
        self.adjustment_converter = adjustment_converter
        self._invoice_cache: dict[tuple[str, UUID], Invoice | None] = {}
        self._credit_cache: dict[tuple[str, UUID], Credit | None] = {}
        self._adjustment_cache: dict[tuple[str, UUID], Adjustment | None] = {}

    @override
    async def create_entity(self, input_data: CheckInput) -> Check:
        return await self.check_service.create_check(input_data)

    @override
    async def to_input(
        self,
        dto: CheckDTO,
        entity_mapping: EntityMapping,
    ) -> ConversionResult[CheckInput]:
        factory_id = entity_mapping.factory_id

        if not factory_id:
            return ConversionResult.fail(FactoryRequiredError())

        check_number = dto.check_number or self._generate_check_number()
        entity_date = dto.check_date or date.today()

        details: list[CheckDetailInput] = []
        for detail in dto.details:
            if detail.flow_detail_index in entity_mapping.skipped_product_indices:
                continue
            check_detail = await self._convert_detail(
                detail, factory_id, entity_mapping
            )
            if check_detail:
                details.append(check_detail)

        entered_commission_amount = sum(
            (detail.applied_amount for detail in details), Decimal("0")
        )

        return ConversionResult.ok(
            CheckInput(
                check_number=check_number,
                entity_date=entity_date,
                factory_id=factory_id,
                entered_commission_amount=entered_commission_amount,
                details=details,
                post_date=dto.post_date,
                commission_month=dto.commission_month,
            )
        )

    async def _convert_detail(
        self,
        detail: CheckDetailDTO,
        factory_id: UUID,
        entity_mapping: EntityMapping,
    ) -> CheckDetailInput | None:
        applied_amount = detail.paid_commission_amount or Decimal("0")

        if applied_amount < 0:
            return await self._convert_negative_detail(
                detail, entity_mapping, applied_amount
            )

        return await self._convert_positive_detail(detail, factory_id, applied_amount)

    async def _convert_positive_detail(
        self,
        detail: CheckDetailDTO,
        factory_id: UUID,
        applied_amount: Decimal,
    ) -> CheckDetailInput:
        invoice_id = None
        if detail.invoice_number:
            invoice = await self._find_invoice_by_number_and_factory(
                detail.invoice_number, factory_id
            )
            if invoice:
                invoice_id = invoice.id
            else:
                logger.warning(
                    f"Invoice {detail.invoice_number} not found for factory {factory_id}"
                )

        return CheckDetailInput(
            applied_amount=applied_amount,
            invoice_id=invoice_id,
        )

    async def _convert_negative_detail(
        self,
        detail: CheckDetailDTO,
        entity_mapping: EntityMapping,
        applied_amount: Decimal,
    ) -> CheckDetailInput | None:
        if detail.order_number:
            return await self._get_or_create_credit_detail(
                detail, entity_mapping, applied_amount
            )
        return await self._get_or_create_adjustment_detail(
            detail, entity_mapping, applied_amount
        )

    async def _get_or_create_credit_detail(
        self,
        detail: CheckDetailDTO,
        entity_mapping: EntityMapping,
        applied_amount: Decimal,
    ) -> CheckDetailInput | None:
        order_id = entity_mapping.get_order_id(detail.flow_detail_index)
        if detail.invoice_number and order_id:
            credit = await self._find_credit_by_number_and_order(
                detail.invoice_number, order_id
            )
            if credit:
                return CheckDetailInput(
                    applied_amount=applied_amount,
                    credit_id=credit.id,
                )

        result = await self.credit_converter.to_input(detail, entity_mapping)
        if result.is_error():
            logger.warning(f"Failed to create credit input: {result.error}")
            return None

        try:
            credit = await self.credit_converter.create_entity(result.unwrap())
            return CheckDetailInput(
                applied_amount=applied_amount,
                credit_id=credit.id,
            )
        except Exception as e:
            logger.warning(f"Failed to create credit: {e}")
            return None

    async def _get_or_create_adjustment_detail(
        self,
        detail: CheckDetailDTO,
        entity_mapping: EntityMapping,
        applied_amount: Decimal,
    ) -> CheckDetailInput | None:
        factory_id = entity_mapping.factory_id
        if detail.invoice_number and factory_id:
            adjustment = await self._find_adjustment_by_number_and_factory(
                detail.invoice_number, factory_id
            )
            if adjustment:
                return CheckDetailInput(
                    applied_amount=applied_amount,
                    adjustment_id=adjustment.id,
                )

        result = await self.adjustment_converter.to_input(detail, entity_mapping)
        if result.is_error():
            logger.warning(f"Failed to create adjustment input: {result.error}")
            return None

        try:
            adjustment = await self.adjustment_converter.create_entity(result.unwrap())
            return CheckDetailInput(
                applied_amount=applied_amount,
                adjustment_id=adjustment.id,
            )
        except Exception as e:
            logger.warning(f"Failed to create adjustment: {e}")
            return None

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

    async def _find_credit_by_number_and_order(
        self,
        credit_number: str,
        order_id: UUID,
    ) -> Credit | None:
        cache_key = (credit_number, order_id)
        if cache_key in self._credit_cache:
            return self._credit_cache[cache_key]

        stmt = (
            select(Credit)
            .options(lazyload("*"))
            .where(
                Credit.credit_number == credit_number,
                Credit.order_id == order_id,
            )
        )
        result = await self.session.execute(stmt)
        credit = result.scalar_one_or_none()

        self._credit_cache[cache_key] = credit
        return credit

    async def _find_adjustment_by_number_and_factory(
        self,
        adjustment_number: str,
        factory_id: UUID,
    ) -> Adjustment | None:
        cache_key = (adjustment_number, factory_id)
        if cache_key in self._adjustment_cache:
            return self._adjustment_cache[cache_key]

        stmt = (
            select(Adjustment)
            .options(lazyload("*"))
            .where(
                Adjustment.adjustment_number == adjustment_number,
                Adjustment.factory_id == factory_id,
            )
        )
        result = await self.session.execute(stmt)
        adjustment = result.scalar_one_or_none()

        self._adjustment_cache[cache_key] = adjustment
        return adjustment

    @staticmethod
    def _generate_check_number() -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"CHK-{timestamp}"
