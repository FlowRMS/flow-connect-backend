"""GraphQL input types for Submittal."""

from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import (
    Submittal,
    SubmittalItem,
    SubmittalItemApprovalStatus,
    SubmittalItemMatchStatus,
    SubmittalStakeholder,
    SubmittalStakeholderRole,
    SubmittalStatus,
    TransmittalPurpose,
)

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.submittals.strawberry.enums import (
    SubmittalItemApprovalStatusGQL,
    SubmittalItemMatchStatusGQL,
    SubmittalStakeholderRoleGQL,
    SubmittalStatusGQL,
    TransmittalPurposeGQL,
)
from app.graphql.submittals.strawberry.submittal_config import SubmittalConfigInput


@strawberry.input
class CreateSubmittalInput(BaseInputGQL[Submittal]):
    """Input for creating a new submittal."""

    submittal_number: str
    quote_id: Optional[UUID] = None
    job_id: Optional[UUID] = None
    status: SubmittalStatusGQL = SubmittalStatusGQL.DRAFT
    transmittal_purpose: Optional[TransmittalPurposeGQL] = None
    description: Optional[str] = None
    config: Optional[SubmittalConfigInput] = None

    def to_orm_model(self) -> Submittal:
        """Convert input to ORM model."""
        config = self.config or SubmittalConfigInput()
        return Submittal(
            submittal_number=self.submittal_number,
            quote_id=self.quote_id,
            job_id=self.job_id,
            status=SubmittalStatus(self.status.value),
            transmittal_purpose=(
                TransmittalPurpose(self.transmittal_purpose.value)
                if self.transmittal_purpose
                else None
            ),
            description=self.description,
            config_include_lamps=config.include_lamps,
            config_include_accessories=config.include_accessories,
            config_include_cq=config.include_cq,
            config_include_from_orders=config.include_from_orders,
            config_roll_up_kits=config.roll_up_kits,
            config_roll_up_accessories=config.roll_up_accessories,
            config_include_zero_quantity_items=config.include_zero_quantity_items,
            config_drop_descriptions=config.drop_descriptions,
            config_drop_line_notes=config.drop_line_notes,
        )


@strawberry.input
class UpdateSubmittalInput:
    """Input for updating a submittal."""

    status: Optional[SubmittalStatusGQL] = None
    transmittal_purpose: Optional[TransmittalPurposeGQL] = None
    description: Optional[str] = None
    job_location: Optional[str] = None
    bid_date: Optional[date] = None
    tags: Optional[list[str]] = None
    config: Optional[SubmittalConfigInput] = None


@strawberry.input
class SubmittalItemInput(BaseInputGQL[SubmittalItem]):
    """Input for creating/updating a submittal item."""

    item_number: int
    quote_detail_id: Optional[UUID] = None
    spec_sheet_id: Optional[UUID] = None
    highlight_version_id: Optional[UUID] = None
    part_number: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Decimal] = None
    approval_status: SubmittalItemApprovalStatusGQL = (
        SubmittalItemApprovalStatusGQL.PENDING
    )
    match_status: SubmittalItemMatchStatusGQL = SubmittalItemMatchStatusGQL.NO_MATCH
    notes: Optional[str] = None

    def to_orm_model(self) -> SubmittalItem:
        """Convert input to ORM model."""
        return SubmittalItem(
            item_number=self.item_number,
            quote_detail_id=self.quote_detail_id,
            spec_sheet_id=self.spec_sheet_id,
            highlight_version_id=self.highlight_version_id,
            part_number=self.part_number,
            description=self.description,
            quantity=self.quantity,
            approval_status=SubmittalItemApprovalStatus(self.approval_status.value),
            match_status=SubmittalItemMatchStatus(self.match_status.value),
            notes=self.notes,
        )


@strawberry.input
class UpdateSubmittalItemInput:
    """Input for updating a submittal item."""

    spec_sheet_id: Optional[UUID] = None
    highlight_version_id: Optional[UUID] = None
    part_number: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Decimal] = None
    approval_status: Optional[SubmittalItemApprovalStatusGQL] = None
    match_status: Optional[SubmittalItemMatchStatusGQL] = None
    notes: Optional[str] = None


@strawberry.input
class SubmittalStakeholderInput(BaseInputGQL[SubmittalStakeholder]):
    """Input for adding a stakeholder to a submittal."""

    role: SubmittalStakeholderRoleGQL
    customer_id: Optional[UUID] = None
    is_primary: bool = False
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    company_name: Optional[str] = None

    def to_orm_model(self) -> SubmittalStakeholder:
        """Convert input to ORM model."""
        return SubmittalStakeholder(
            role=SubmittalStakeholderRole(self.role.value),
            customer_id=self.customer_id,
            is_primary=self.is_primary,
            contact_name=self.contact_name,
            contact_email=self.contact_email,
            contact_phone=self.contact_phone,
            company_name=self.company_name,
        )


@strawberry.input
class SendSubmittalEmailInput:
    """Input for sending a submittal email."""

    submittal_id: UUID
    revision_id: Optional[UUID] = None
    subject: str
    body: Optional[str] = None
    recipient_emails: list[str]


@strawberry.input
class GenerateSubmittalPdfInput:
    """Input for generating a submittal PDF."""

    submittal_id: UUID
    output_type: str = "pdf"  # 'pdf', 'email', 'email_link'

    # Include options
    include_cover_page: bool = True
    include_transmittal_page: bool = True
    include_fixture_summary: bool = True
    include_pages: bool = True
    include_type_cover_page: bool = False

    # Display options
    show_quantities: bool = False
    show_descriptions: bool = True
    show_lead_times: bool = False
    hide_notes: bool = False
    use_customer_logo: bool = True

    # Finishing options
    print_duplex: bool = False
    cap_file_size_mb: Optional[int] = None

    # Transmittal options
    attached_items: Optional[list[str]] = None  # 'drawings', 'specifications', etc.
    attached_other: Optional[str] = None
    transmitted_for: Optional[list[str]] = None  # 'prior_approval', 'approval', etc.
    transmitted_for_other: Optional[str] = None
    copies: int = 1

    # Selected items to include
    selected_item_ids: Optional[list[UUID]] = None

    # Addressed to stakeholder IDs
    addressed_to_ids: Optional[list[UUID]] = None

    # Create new revision after generating?
    create_revision: bool = True
    revision_notes: Optional[str] = None
