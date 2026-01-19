import json
from datetime import date
from decimal import Decimal
from typing import Any, Self

import strawberry
from commons.db.v6.crm.quotes import (
    PipelineStage,
    QuoteStatus,
)
from sqlalchemy.engine.row import Row

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type
class SalesRepSummary:
    full_name: str
    total: Decimal
    avg_split_rate: Decimal

    @classmethod
    def from_json_list(cls, json_data: list[dict[str, Any]] | None) -> list[Self]:
        if not json_data:
            return []
        return [
            cls(
                full_name=item["full_name"],
                total=Decimal(str(item["total"])),
                avg_split_rate=Decimal(str(item["avg_split_rate"])),
            )
            for item in json_data
        ]


@strawberry.type(name="QuoteLandingPage")
class QuoteLandingPageResponse(LandingPageInterfaceBase):
    quote_number: str
    status: QuoteStatus
    pipeline_stage: PipelineStage
    entity_date: date
    exp_date: date | None
    total: Decimal
    commission: Decimal | None
    published: bool
    sold_to_customer_name: str
    end_users: list[str]
    factories: list[str]
    categories: list[str] | None
    part_numbers: list[str] | None
    sales_reps: list[SalesRepSummary]

    @classmethod
    def from_orm_model(cls, row: Row[Any]) -> Self:
        data = cls.unpack_row(row)
        sales_reps_json = data.pop("sales_reps", None)
        if isinstance(sales_reps_json, str):
            sales_reps_json = json.loads(sales_reps_json)
        data["sales_reps"] = SalesRepSummary.from_json_list(sales_reps_json)
        return cls(**data)
