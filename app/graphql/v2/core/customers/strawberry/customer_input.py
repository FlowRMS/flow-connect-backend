from uuid import UUID

import strawberry

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.v2.core.customers.models import CustomerV2


@strawberry.input
class CustomerInput(BaseInputGQL[CustomerV2]):
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

    def to_orm_model(self) -> CustomerV2:
        return CustomerV2(
            company_name=self.company_name,
            published=self.published,
            is_parent=self.is_parent,
            parent_id=self.parent_id,
            contact_email=self.contact_email,
            contact_number=self.contact_number,
            customer_branch_id=self.customer_branch_id,
            customer_territory_id=self.customer_territory_id,
            logo_url=self.logo_url,
            inside_rep_id=self.inside_rep_id,
            type=self.type,
        )
