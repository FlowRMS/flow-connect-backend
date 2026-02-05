from collections import defaultdict
from decimal import Decimal
from typing import TypedDict
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.commission import Check, CheckDetail

from app.graphql.checks.repositories.checks_repository import ChecksRepository
from app.graphql.checks.services.posted_statement_excel_service import (
    PostedStatementExcelService,
)
from app.graphql.checks.strawberry.posted_statement_response import (
    PostedStatementDetailResponse,
    PostedStatementHeaderResponse,
    PostedStatementRepSummaryResponse,
    PostedStatementResponse,
)
from app.graphql.v2.files.services.file_upload_service import FileUploadService


class _RepTotal(TypedDict):
    expected: Decimal
    received: Decimal
    name: str


class _RepSummaryEntry(TypedDict):
    expected: Decimal
    received: Decimal
    name: str
    id: UUID


class PostedStatementService:
    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        checks_repository: ChecksRepository,
        file_upload_service: FileUploadService,
        posted_statement_excel_service: PostedStatementExcelService,
        auth_info: AuthInfo,
    ) -> None:
        self.checks_repository = checks_repository
        self.file_upload_service = file_upload_service
        self.excel_service = posted_statement_excel_service
        self.auth_info = auth_info

    async def generate_posted_statement(
        self, check_id: UUID
    ) -> PostedStatementResponse:
        check = await self.checks_repository.find_check_by_id(check_id)
        header = self._build_header(check)
        details = self._build_details(check)
        rep_summaries = self._build_rep_summaries(details)
        excel_bytes = self.excel_service.generate_excel(
            check, header, rep_summaries, details
        )
        upload_result = await self.file_upload_service.upload_file(
            file_content=excel_bytes,
            file_name=f"posted_statement_{check.check_number}.xlsx",
            folder_path=f"statements/{self.auth_info.tenant_id}",
        )
        return PostedStatementResponse(
            header=header,
            rep_summaries=rep_summaries,
            details=details,
            presigned_url=upload_result.presigned_url,
        )

    def _build_header(self, check: Check) -> PostedStatementHeaderResponse:
        return PostedStatementHeaderResponse(
            check_number=check.check_number,
            post_date=check.post_date or check.entity_date,
            entity_date=check.entity_date,
            commission_month=check.commission_month,
            commission_amount=check.entered_commission_amount,
            factory_id=check.factory_id,
            factory_name=check.factory.title,
        )

    def _build_details(self, check: Check) -> list[PostedStatementDetailResponse]:
        details: list[PostedStatementDetailResponse] = []
        for check_detail in check.details:
            details.extend(self._process_check_detail(check, check_detail))
        return details

    def _process_check_detail(
        self, check: Check, check_detail: CheckDetail
    ) -> list[PostedStatementDetailResponse]:
        if check_detail.invoice:
            return self._process_invoice_detail(check, check_detail)
        if check_detail.adjustment:
            return self._process_adjustment_detail(check, check_detail)
        if check_detail.credit:
            return self._process_credit_detail(check, check_detail)
        return []

    def _process_invoice_detail(
        self, check: Check, check_detail: CheckDetail
    ) -> list[PostedStatementDetailResponse]:
        invoice = check_detail.invoice
        if not invoice:
            return []

        order_number = invoice.order.order_number if invoice.order else None
        sales_amount = invoice.balance.total if invoice.balance else Decimal(0)
        total_invoice_commission = (
            invoice.balance.commission if invoice.balance else Decimal(0)
        )

        rep_totals: dict[UUID, _RepTotal] = {}
        for invoice_detail in invoice.details:
            detail_commission = invoice_detail.commission or Decimal(0)
            detail_proportion = (
                detail_commission / total_invoice_commission
                if total_invoice_commission > 0
                else Decimal(0)
            )
            for split_rate in invoice_detail.outside_split_rates:
                rate = (split_rate.split_rate or Decimal(100)) / Decimal(100)
                expected = detail_commission * rate
                received = check_detail.applied_amount * detail_proportion * rate
                rep_id = split_rate.user_id
                if rep_id not in rep_totals:
                    rep_totals[rep_id] = _RepTotal(
                        expected=Decimal(0),
                        received=Decimal(0),
                        name=split_rate.user.full_name,
                    )
                rep_totals[rep_id]["expected"] += expected
                rep_totals[rep_id]["received"] += received

        return [
            PostedStatementDetailResponse(
                entity_number=invoice.invoice_number,
                entity_type="Invoice",
                expected_commission=data["expected"],
                commission_received=data["received"].quantize(Decimal("0.01")),
                outside_sales_rep_id=rep_id,
                outside_sales_rep_name=data["name"],
                factory_name=check.factory.title,
                posted_month=check.post_date,
                commission_month=check.commission_month,
                order_number=order_number,
                sales_amount=sales_amount,
            )
            for rep_id, data in rep_totals.items()
        ]

    def _process_adjustment_detail(
        self, check: Check, check_detail: CheckDetail
    ) -> list[PostedStatementDetailResponse]:
        details: list[PostedStatementDetailResponse] = []
        adjustment = check_detail.adjustment
        if not adjustment:
            return details

        for split_rate in adjustment.split_rates:
            rate = (split_rate.split_rate or Decimal(100)) / Decimal(100)
            expected = adjustment.amount * rate
            received = check_detail.applied_amount * rate
            details.append(
                PostedStatementDetailResponse(
                    entity_number=adjustment.adjustment_number,
                    entity_type="Adjustment",
                    expected_commission=expected,
                    commission_received=received,
                    outside_sales_rep_id=split_rate.user_id,
                    outside_sales_rep_name=split_rate.user.full_name,
                    factory_name=check.factory.title,
                    posted_month=check.post_date,
                    commission_month=check.commission_month,
                    order_number=None,
                    sales_amount=adjustment.amount,
                )
            )
        return details

    def _process_credit_detail(
        self, check: Check, check_detail: CheckDetail
    ) -> list[PostedStatementDetailResponse]:
        credit = check_detail.credit
        if not credit:
            return []

        order_number = credit.order.order_number if credit.order else None
        sales_amount = credit.balance.total if credit.balance else Decimal(0)
        total_credit_commission = (
            credit.balance.commission if credit.balance else Decimal(0)
        )

        rep_totals: dict[UUID, _RepTotal] = {}
        for credit_detail in credit.details:
            detail_commission = credit_detail.commission or Decimal(0)
            detail_proportion = (
                detail_commission / total_credit_commission
                if total_credit_commission > 0
                else Decimal(0)
            )
            for split_rate in credit_detail.outside_split_rates:
                rate = (split_rate.split_rate or Decimal(100)) / Decimal(100)
                expected = detail_commission * rate
                received = check_detail.applied_amount * detail_proportion * rate
                rep_id = split_rate.user_id
                if rep_id not in rep_totals:
                    rep_totals[rep_id] = _RepTotal(
                        expected=Decimal(0),
                        received=Decimal(0),
                        name=split_rate.user.full_name,
                    )
                rep_totals[rep_id]["expected"] += expected
                rep_totals[rep_id]["received"] += received

        return [
            PostedStatementDetailResponse(
                entity_number=credit.credit_number,
                entity_type="Credit",
                expected_commission=Decimal("-1") * data["expected"],
                commission_received=(Decimal("-1") * data["received"]).quantize(
                    Decimal("0.01")
                ),
                outside_sales_rep_id=rep_id,
                outside_sales_rep_name=data["name"],
                factory_name=check.factory.title,
                posted_month=check.post_date,
                commission_month=check.commission_month,
                order_number=order_number,
                sales_amount=sales_amount,
            )
            for rep_id, data in rep_totals.items()
        ]

    def _build_rep_summaries(
        self, details: list[PostedStatementDetailResponse]
    ) -> list[PostedStatementRepSummaryResponse]:
        summaries: dict[UUID, _RepSummaryEntry] = defaultdict(
            lambda: _RepSummaryEntry(
                expected=Decimal(0),
                received=Decimal(0),
                name="",
                id=UUID(int=0),
            )
        )
        for detail in details:
            rep_id = detail.outside_sales_rep_id
            summaries[rep_id]["expected"] += detail.expected_commission
            summaries[rep_id]["received"] += detail.commission_received
            summaries[rep_id]["name"] = detail.outside_sales_rep_name
            summaries[rep_id]["id"] = rep_id
        return [
            PostedStatementRepSummaryResponse(
                outside_sales_rep_id=data["id"],
                outside_sales_rep_name=data["name"],
                expected_commission=data["expected"],
                commission_received=data["received"],
            )
            for data in summaries.values()
        ]
