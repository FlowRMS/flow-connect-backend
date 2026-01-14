from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

import strawberry


@strawberry.type
@dataclass
class PostedStatementHeaderResponse:
    check_number: str
    post_date: date
    entity_date: date
    commission_month: date | None
    commission_amount: Decimal | None
    factory_id: UUID
    factory_name: str


@strawberry.type
@dataclass
class PostedStatementRepSummaryResponse:
    outside_sales_rep_id: UUID
    outside_sales_rep_name: str
    expected_commission: Decimal
    commission_received: Decimal


@strawberry.type
@dataclass
class PostedStatementDetailResponse:
    entity_number: str
    entity_type: str
    expected_commission: Decimal
    commission_received: Decimal
    outside_sales_rep_id: UUID
    outside_sales_rep_name: str
    factory_name: str
    posted_month: date | None
    commission_month: date | None
    order_number: str | None
    sales_amount: Decimal


@strawberry.type
@dataclass
class PostedStatementResponse:
    header: PostedStatementHeaderResponse
    rep_summaries: list[PostedStatementRepSummaryResponse]
    details: list[PostedStatementDetailResponse]
    presigned_url: str


@strawberry.type
@dataclass
class PostedStatementSummaryResponse:
    paid_commissions: Decimal
    credits: Decimal
    expenses: Decimal
    applied_total: Decimal
    expected_commission: Decimal
    adjusted_expected_commission: Decimal
    balance: Decimal
