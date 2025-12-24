from uuid import UUID

import strawberry
from commons.db.v6 import Customer

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.v2.core.customers.strawberry.customer_split_rate_input import (
    CustomerSplitRateInput,
)


@strawberry.input
class CustomerInput(BaseInputGQL[Customer]):
    company_name: str
    split_rates: list[CustomerSplitRateInput] = strawberry.field(default_factory=list)
    published: bool = False
    is_parent: bool = False
    parent_id: UUID | None = None
    contact_email: str | None = None
    contact_number: str | None = None

    def to_orm_model(self) -> Customer:
        return Customer(
            company_name=self.company_name,
            published=self.published,
            is_parent=self.is_parent,
            parent_id=self.parent_id,
            contact_email=self.contact_email,
            contact_number=self.contact_number,
            split_rates=[rate.to_orm_model() for rate in self.split_rates],
        )
