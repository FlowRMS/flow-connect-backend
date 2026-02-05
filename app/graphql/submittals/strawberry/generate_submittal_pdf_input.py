from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import SubmittalRevision

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class GenerateSubmittalPdfInput(BaseInputGQL[SubmittalRevision]):
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
    save_as_attachment: bool = False
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
