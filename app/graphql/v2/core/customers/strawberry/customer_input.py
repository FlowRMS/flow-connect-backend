from uuid import UUID

import strawberry
from commons.db.v6 import Customer

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class CustomerInput(BaseInputGQL[Customer]):
    company_name: str
    published: bool = False
    is_parent: bool = False
    parent_id: UUID | None = None
    contact_email: str | None = None
    contact_number: str | None = None
    customer_branch_id: UUID | None = None
    customer_territory_id: UUID | None = None
    logo_url: str | None = None
    inside_rep_id: UUID | None = None
    type: str | None = None

    def to_orm_model(self) -> Customer:
        return Customer(
            company_name=self.company_name,
            published=self.published,
            is_parent=self.is_parent,
            parent_id=self.parent_id,  # pyright: ignore[reportCallIssue]
            contact_email=self.contact_email,
            contact_number=self.contact_number,
        )
