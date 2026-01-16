from uuid import UUID

import strawberry
from commons.db.v6 import Customer

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.v2.core.customers.strawberry.customer_split_rate_input import (
    InsideSplitRateInput,
    OutsideSplitRateInput,
)


@strawberry.input
class CustomerInput(BaseInputGQL[Customer]):
    company_name: str
    inside_split_rates: list[InsideSplitRateInput] = strawberry.field(
        default_factory=list
    )
    outside_split_rates: list[OutsideSplitRateInput] = strawberry.field(
        default_factory=list
    )
    published: bool = False
    is_parent: bool = False
    parent_id: UUID | None = None
    buying_group_id: UUID | None = None
    territory_id: UUID | None = None

    def to_orm_model(self) -> Customer:
        split_rates = [rate.to_orm_model() for rate in self.inside_split_rates] + [
            rate.to_orm_model() for rate in self.outside_split_rates
        ]

        return Customer(
            company_name=self.company_name,
            published=self.published,
            is_parent=self.is_parent,
            parent_id=self.parent_id,
            buying_group_id=self.buying_group_id,
            territory_id=self.territory_id,
            split_rates=split_rates,
        )
