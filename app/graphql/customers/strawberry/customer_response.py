"""GraphQL response type for Customer."""

from typing import Self
from uuid import UUID

import strawberry
from commons.db.models import Customer

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class CustomerResponse(DTOMixin[Customer]):
    id: UUID
    company_name: str
    parent_id: UUID | None
    inside_rep_id: UUID | None

    @classmethod
    def from_orm_model(cls, model: Customer) -> Self:
        return cls(
            id=model.id,
            company_name=model.company_name,
            parent_id=model.parent_id,
            inside_rep_id=model.inside_rep_id,
        )

    @strawberry.field
    def url(self) -> str:
        return f"/core/customers/list/{self.id}"
