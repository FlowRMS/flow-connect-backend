from datetime import date
from decimal import Decimal
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
from strawberry import UNSET

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
    submittal_number: str
    quote_id: UUID | None = None
    job_id: UUID | None = None
    status: SubmittalStatusGQL = SubmittalStatusGQL.DRAFT
    transmittal_purpose: TransmittalPurposeGQL | None = None
    description: str | None = None
    config: SubmittalConfigInput | None = None

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
    status: SubmittalStatusGQL | None = None
    transmittal_purpose: TransmittalPurposeGQL | None = None
    description: str | None = None
    job_location: str | None = None
    bid_date: date | None = None
    tags: list[str] | None = None
    config: SubmittalConfigInput | None = None


@strawberry.input
class SubmittalItemInput(BaseInputGQL[SubmittalItem]):
    item_number: int
    quote_detail_id: UUID | None = None
    spec_sheet_id: UUID | None = None
    highlight_version_id: UUID | None = None
    part_number: str | None = None
    manufacturer: str | None = None
    description: str | None = None
    quantity: Decimal | None = None
    approval_status: SubmittalItemApprovalStatusGQL = (
        SubmittalItemApprovalStatusGQL.PENDING
    )
    match_status: SubmittalItemMatchStatusGQL = SubmittalItemMatchStatusGQL.NO_MATCH
    notes: str | None = None

    def to_orm_model(self) -> SubmittalItem:
        """Convert input to ORM model."""
        return SubmittalItem(
            item_number=self.item_number,
            quote_detail_id=self.quote_detail_id,
            spec_sheet_id=self.spec_sheet_id,
            highlight_version_id=self.highlight_version_id,
            part_number=self.part_number,
            manufacturer=self.manufacturer,
            description=self.description,
            quantity=self.quantity,
            approval_status=SubmittalItemApprovalStatus(self.approval_status.value),
            match_status=SubmittalItemMatchStatus(self.match_status.value),
            notes=self.notes,
        )


@strawberry.input
class UpdateSubmittalItemInput:
    # Use UNSET to distinguish "not provided" from "null"
    spec_sheet_id: UUID | None = UNSET  # type: ignore[assignment]
    highlight_version_id: UUID | None = UNSET  # type: ignore[assignment]
    part_number: str | None = None
    manufacturer: str | None = None
    description: str | None = None
    quantity: Decimal | None = None
    approval_status: SubmittalItemApprovalStatusGQL | None = None
    match_status: SubmittalItemMatchStatusGQL | None = None
    notes: str | None = None


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
    submittal_id: UUID
    revision_id: UUID | None = None
    subject: str
    body: str | None = None
    recipient_emails: list[str]
    attachment_url: str | None = None
    attachment_name: str | None = None


@strawberry.input
class GenerateSubmittalPdfInput:
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
    cap_file_size_mb: int | None = None

    # Transmittal options
    attached_items: list[str] | None = None  # 'drawings', 'specifications', etc.
    attached_other: str | None = None
    transmitted_for: list[str] | None = None  # 'prior_approval', 'approval', etc.
    transmitted_for_other: str | None = None
    copies: int = 1

    # Selected items to include
    selected_item_ids: list[UUID] | None = None

    # Addressed to stakeholder IDs
    addressed_to_ids: list[UUID] | None = None

    # Create new revision after generating?
    create_revision: bool = True
    revision_notes: str | None = None
