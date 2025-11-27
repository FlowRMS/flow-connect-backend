"""GraphQL response type for PreOpportunity."""

from datetime import date, datetime
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.pre_opportunities.models.pre_opportunity_model import PreOpportunity
from app.graphql.pre_opportunities.models.pre_opportunity_status import (
    PreOpportunityStatus,
)
from app.graphql.pre_opportunities.strawberry.pre_opportunity_balance_response import (
    PreOpportunityBalanceResponse,
)
from app.graphql.pre_opportunities.strawberry.pre_opportunity_detail_response import (
    PreOpportunityDetailResponse,
)


@strawberry.type
class PreOpportunityResponse(DTOMixin[PreOpportunity]):
    """Complete pre-opportunity with balance and details."""

    id: UUID
    created_at: datetime
    created_by: UUID
    status: PreOpportunityStatus
    entity_number: str
    entity_date: date
    exp_date: date | None
    revise_date: date | None
    accept_date: date | None
    sold_to_customer_id: UUID
    sold_to_customer_address_id: UUID | None
    bill_to_customer_id: UUID | None
    bill_to_customer_address_id: UUID | None
    job_id: UUID | None
    payment_terms: str | None
    customer_ref: str | None
    freight_terms: str | None
    balance: PreOpportunityBalanceResponse
    details: list[PreOpportunityDetailResponse]

    @classmethod
    def from_orm_model(cls, model: PreOpportunity) -> "PreOpportunityResponse":
        """Convert ORM model to GraphQL type."""
        return cls(
            id=model.id,
            created_at=model.created_at,
            created_by=model.created_by,
            status=model.status,
            entity_number=model.entity_number,
            entity_date=model.entity_date,
            exp_date=model.exp_date,
            revise_date=model.revise_date,
            accept_date=model.accept_date,
            sold_to_customer_id=model.sold_to_customer_id,
            sold_to_customer_address_id=model.sold_to_customer_address_id,
            bill_to_customer_id=model.bill_to_customer_id,
            bill_to_customer_address_id=model.bill_to_customer_address_id,
            job_id=model.job_id,
            payment_terms=model.payment_terms,
            customer_ref=model.customer_ref,
            freight_terms=model.freight_terms,
            balance=PreOpportunityBalanceResponse.from_orm_model(model.balance),
            details=PreOpportunityDetailResponse.from_orm_model_list(model.details),
        )
