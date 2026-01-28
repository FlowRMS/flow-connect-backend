from datetime import date, datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.common.creation_type import CreationType
from commons.db.v6.crm.quotes import (
    PipelineStage,
    Quote,
    QuoteStatus,
)

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class QuoteLiteResponse(DTOMixin[Quote]):
    _instance: strawberry.Private[Quote]
    id: UUID
    created_at: datetime
    created_by_id: UUID
    quote_number: str
    name: str | None
    entity_date: date
    status: QuoteStatus
    pipeline_stage: PipelineStage
    published: bool
    creation_type: CreationType
    sold_to_customer_id: UUID | None
    factory_per_line_item: bool
    name: str | None
    bill_to_customer_id: UUID | None
    payment_terms: str | None
    customer_ref: str | None
    freight_terms: str | None
    exp_date: date | None
    revise_date: date | None
    accept_date: date | None
    blanket: bool
    duplicated_from: UUID | None
    version_of: UUID | None
    balance_id: UUID
    inside_per_line_item: bool | None
    outside_per_line_item: bool | None
    end_user_per_line_item: bool | None
    name: str | None

    @classmethod
    def from_orm_model(cls, model: Quote) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            created_at=model.created_at,
            created_by_id=model.created_by_id,
            quote_number=model.quote_number,
            name=model.name,
            entity_date=model.entity_date,
            factory_per_line_item=model.factory_per_line_item,
            status=model.status,
            pipeline_stage=model.pipeline_stage,
            published=model.published,
            creation_type=model.creation_type,
            sold_to_customer_id=model.sold_to_customer_id,
            name=model.name,
            bill_to_customer_id=model.bill_to_customer_id,
            payment_terms=model.payment_terms,
            customer_ref=model.customer_ref,
            freight_terms=model.freight_terms,
            exp_date=model.exp_date,
            revise_date=model.revise_date,
            accept_date=model.accept_date,
            blanket=model.blanket,
            duplicated_from=model.duplicated_from,
            version_of=model.version_of,
            balance_id=model.balance_id,
            inside_per_line_item=model.inside_per_line_item,
            outside_per_line_item=model.outside_per_line_item,
            end_user_per_line_item=model.end_user_per_line_item,
            name=getattr(model, "name", None),
        )

    @strawberry.field
    def url(self) -> str:
        return f"/crm/quotes/list/{self.id}"
