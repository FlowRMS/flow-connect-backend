"""GraphQL response type for SubmittalStakeholder."""

from typing import Optional, Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import SubmittalStakeholder

from app.core.db.adapters.dto import DTOMixin
from app.graphql.submittals.strawberry.enums import SubmittalStakeholderRoleGQL


@strawberry.type
class SubmittalStakeholderResponse(DTOMixin[SubmittalStakeholder]):
    """Response type for SubmittalStakeholder."""

    _instance: strawberry.Private[SubmittalStakeholder]
    id: UUID
    submittal_id: UUID
    customer_id: Optional[UUID]
    role: SubmittalStakeholderRoleGQL
    is_primary: bool
    contact_name: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    company_name: Optional[str]

    @classmethod
    def from_orm_model(cls, model: SubmittalStakeholder) -> Self:
        """Convert ORM model to GraphQL response."""
        return cls(
            _instance=model,
            id=model.id,
            submittal_id=model.submittal_id,
            customer_id=model.customer_id,
            role=SubmittalStakeholderRoleGQL(model.role.value),
            is_primary=model.is_primary,
            contact_name=model.contact_name,
            contact_email=model.contact_email,
            contact_phone=model.contact_phone,
            company_name=model.company_name,
        )
