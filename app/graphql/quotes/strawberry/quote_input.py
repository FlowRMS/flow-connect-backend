from datetime import date
from uuid import UUID

import strawberry
from commons.db.v6.common.creation_type import CreationType
from commons.db.v6.crm.quotes import (
    PipelineStage,
    Quote,
    QuoteStatus,
)

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.quotes.strawberry.quote_detail_input import QuoteDetailInput


@strawberry.input
class QuoteInput(BaseInputGQL[Quote]):
    quote_number: str
    entity_date: date
    sold_to_customer_id: UUID
    status: QuoteStatus
    pipeline_stage: PipelineStage
    details: list[QuoteDetailInput]

    id: UUID | None = strawberry.UNSET
    job_id: UUID | None = strawberry.UNSET
    published: bool = strawberry.UNSET
    creation_type: CreationType = strawberry.UNSET
    bill_to_customer_id: UUID | None = strawberry.UNSET
    payment_terms: str | None = strawberry.UNSET
    customer_ref: str | None = strawberry.UNSET
    freight_terms: str | None = strawberry.UNSET
    exp_date: date | None = strawberry.UNSET
    revise_date: date | None = strawberry.UNSET
    accept_date: date | None = strawberry.UNSET
    blanket: bool = strawberry.UNSET

    def to_orm_model(self) -> Quote:
        published = self.published if self.published != strawberry.UNSET else False
        creation_type = (
            self.creation_type
            if self.creation_type != strawberry.UNSET
            else CreationType.MANUAL
        )
        blanket = self.blanket if self.blanket != strawberry.UNSET else False

        return Quote(
            quote_number=self.quote_number,
            entity_date=self.entity_date,
            sold_to_customer_id=self.sold_to_customer_id,
            job_id=self.optional_field(self.job_id),
            status=self.status,
            pipeline_stage=self.pipeline_stage,
            published=published,
            creation_type=creation_type,
            bill_to_customer_id=self.optional_field(self.bill_to_customer_id),
            payment_terms=self.optional_field(self.payment_terms),
            customer_ref=self.optional_field(self.customer_ref),
            freight_terms=self.optional_field(self.freight_terms),
            exp_date=self.optional_field(self.exp_date),
            revise_date=self.optional_field(self.revise_date),
            accept_date=self.optional_field(self.accept_date),
            blanket=blanket,
            details=[detail.to_orm_model() for detail in self.details],
        )
