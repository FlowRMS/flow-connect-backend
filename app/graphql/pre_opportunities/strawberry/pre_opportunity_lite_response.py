"""GraphQL response type for PreOpportunity lite version without balance and details."""

from datetime import date, datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.pre_opportunities.pre_opportunity_model import PreOpportunity
from commons.db.v6.crm.pre_opportunities.pre_opportunity_status import (
    PreOpportunityStatus,
)

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class PreOpportunityLiteResponse(DTOMixin[PreOpportunity]):
    _instance: strawberry.Private[PreOpportunity]
    id: UUID
    created_at: datetime
    created_by_id: UUID
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
    tags: list[str] | None

    @classmethod
    def from_orm_model(cls, model: PreOpportunity) -> Self:
        """Convert ORM model to GraphQL type."""
        return cls(
            _instance=model,
            id=model.id,
            created_at=model.created_at,
            created_by_id=model.created_by_id,
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
            tags=model.tags,
        )
