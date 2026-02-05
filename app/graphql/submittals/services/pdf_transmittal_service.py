from datetime import datetime
from typing import Any

from commons.db.v6.crm.submittals import Submittal, SubmittalStakeholder
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from app.graphql.submittals.strawberry.generate_submittal_pdf_input import (
    GenerateSubmittalPdfInput,
)


class PdfTransmittalService:
    """Service for generating transmittal page elements."""

    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        styles: Any,
    ) -> None:
        self.styles = styles

    def add_attached_section(
        self, elements: list, input_data: GenerateSubmittalPdfInput
    ) -> None:
        """Add attached items section to the transmittal page."""
        attached_labels = {
            "drawings": "Drawings",
            "specifications": "Specifications",
            "prints": "Prints",
            "information": "Information",
            "plans": "Plans",
            "submittals": "Submittals",
        }
        if input_data.attached_items or input_data.attached_other:
            elements.append(Paragraph("Attached:", self.styles["Normal"]))
            parts = []
            if input_data.attached_items:
                parts.extend(
                    attached_labels.get(item, item.replace("_", " ").title())
                    for item in input_data.attached_items
                )
            if input_data.attached_other:
                parts.append(input_data.attached_other)
            elements.append(Paragraph(", ".join(parts), self.styles["ItemDescription"]))
            elements.append(Spacer(1, 0.15 * inch))

    def add_transmitted_for_section(
        self, elements: list, input_data: GenerateSubmittalPdfInput
    ) -> None:
        """Add transmitted for section to the transmittal page."""
        transmitted_for_labels = {
            "prior_approval": "Prior Approval",
            "resubmit_for_approval": "Resubmittal for Approval",
            "record": "Record",
            "approval": "Approval",
            "corrections": "Corrections",
            "bids_due_on": "Bids Due On",
            "approval_as_submitted": "Approval as Submitted",
            "for_your_use": "Your Use",
            "approval_as_noted": "Approval as Noted",
            "review_and_comment": "Review and Comment",
        }
        if input_data.transmitted_for or input_data.transmitted_for_other:
            elements.append(Paragraph("Transmitted For:", self.styles["Normal"]))
            parts = []
            if input_data.transmitted_for:
                parts.extend(
                    transmitted_for_labels.get(item, item.replace("_", " ").title())
                    for item in input_data.transmitted_for
                )
            if input_data.transmitted_for_other:
                parts.append(input_data.transmitted_for_other)
            elements.append(Paragraph(", ".join(parts), self.styles["ItemDescription"]))
            elements.append(Spacer(1, 0.15 * inch))

    def add_addressed_to_section(
        self, elements: list, addressed_to: list[SubmittalStakeholder]
    ) -> None:
        """Add addressed to section to the transmittal page."""
        if addressed_to:
            elements.append(Paragraph("Addressed To:", self.styles["Normal"]))
            for s in addressed_to:
                name = s.contact_name or "Unknown"
                company = s.company_name or ""
                line = name
                if company:
                    line += f" ({company})"
                elements.append(Paragraph(line, self.styles["ItemDescription"]))
            elements.append(Spacer(1, 0.25 * inch))

    def build_info_table(
        self,
        submittal: Submittal,
        items_count: int,
        input_data: GenerateSubmittalPdfInput,
    ) -> Table:
        """Build the info table for the transmittal page."""
        info_data = [
            ["Submittal #:", submittal.submittal_number],
            ["Date:", datetime.now().strftime("%B %d, %Y")],
            ["Number of Items:", str(items_count)],
        ]
        if input_data.copies > 1:
            info_data.append(["Copies:", str(input_data.copies)])

        info_table = Table(info_data, colWidths=[1.5 * inch, 4 * inch])
        info_table.setStyle(
            TableStyle(
                [
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        return info_table
