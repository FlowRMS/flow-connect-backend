from datetime import date
from uuid import UUID

import strawberry
from commons.db.v6.crm.pre_opportunities.pre_opportunity_model import PreOpportunity
from commons.db.v6.crm.pre_opportunities.pre_opportunity_status import (
    PreOpportunityStatus,
)

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.pre_opportunities.strawberry.pre_opportunity_detail_input import (
    PreOpportunityDetailInput,
)


@strawberry.input
class PreOpportunityInput(BaseInputGQL[PreOpportunity]):
    """Input for creating/updating a pre-opportunity."""

    status: PreOpportunityStatus
    entity_number: str
    entity_date: date
    sold_to_customer_id: UUID
    details: list[PreOpportunityDetailInput]

    id: UUID | None = strawberry.UNSET
    exp_date: date | None = strawberry.UNSET
    revise_date: date | None = strawberry.UNSET
    accept_date: date | None = strawberry.UNSET
    sold_to_customer_address_id: UUID | None = strawberry.UNSET
    bill_to_customer_id: UUID | None = strawberry.UNSET
    bill_to_customer_address_id: UUID | None = strawberry.UNSET
    job_id: UUID | None = strawberry.UNSET
    payment_terms: str | None = strawberry.UNSET
    customer_ref: str | None = strawberry.UNSET
    freight_terms: str | None = strawberry.UNSET
    tags: list[str] | None = strawberry.UNSET

    def to_orm_model(self) -> PreOpportunity:
        return PreOpportunity(
            status=self.status,
            entity_number=self.entity_number,
            entity_date=self.entity_date,
            sold_to_customer_id=self.sold_to_customer_id,
            exp_date=self.optional_field(self.exp_date),
            revise_date=self.optional_field(self.revise_date),
            accept_date=self.optional_field(self.accept_date),
            sold_to_customer_address_id=self.optional_field(
                self.sold_to_customer_address_id
            ),
            bill_to_customer_id=self.optional_field(self.bill_to_customer_id),
            bill_to_customer_address_id=self.optional_field(
                self.bill_to_customer_address_id
            ),
            job_id=self.optional_field(self.job_id),
            payment_terms=self.optional_field(self.payment_terms),
            customer_ref=self.optional_field(self.customer_ref),
            freight_terms=self.optional_field(self.freight_terms),
            tags=self.optional_field(self.tags),
            details=[detail.to_orm_model() for detail in self.details],
        )
