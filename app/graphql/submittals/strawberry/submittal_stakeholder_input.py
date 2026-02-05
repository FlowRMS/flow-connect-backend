from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import SubmittalStakeholder, SubmittalStakeholderRole

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.submittals.strawberry.enums import SubmittalStakeholderRoleGQL


@strawberry.input
class SubmittalStakeholderInput(BaseInputGQL[SubmittalStakeholder]):
    role: SubmittalStakeholderRoleGQL
    customer_id: UUID | None = None
    is_primary: bool = False
    contact_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    company_name: str | None = None

    def to_orm_model(self) -> SubmittalStakeholder:
        return SubmittalStakeholder(
            role=SubmittalStakeholderRole(self.role.value),
            customer_id=self.customer_id,
            is_primary=self.is_primary,
            contact_name=self.contact_name,
            contact_email=self.contact_email,
            contact_phone=self.contact_phone,
            company_name=self.company_name,
        )
