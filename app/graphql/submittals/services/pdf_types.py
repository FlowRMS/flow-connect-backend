from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from commons.db.v6.crm.submittals.enums import SubmittalItemApprovalStatus


@dataclass
class PdfGenerationResult:
    success: bool
    pdf_bytes: bytes | None = None
    file_name: str | None = None
    file_size_bytes: int = 0
    error: str | None = None


@dataclass
class RolledUpItem:
    id: UUID | None = None
    item_number: int = 0
    part_number: str | None = None
    manufacturer: str | None = None
    description: str | None = None
    quantity: Decimal | None = None
    approval_status: SubmittalItemApprovalStatus = SubmittalItemApprovalStatus.PENDING
    notes: str | None = None
    lead_time: str | None = None
    spec_sheet_id: UUID | None = None
    rolled_up_count: int = 0
