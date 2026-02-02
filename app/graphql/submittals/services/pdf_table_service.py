import io
from datetime import datetime
from typing import TYPE_CHECKING

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

if TYPE_CHECKING:
    from reportlab.platypus.flowables import Flowable

from commons.db.v6.crm.submittals import Submittal, SubmittalItem, SubmittalStakeholder

from app.graphql.submittals.services.pdf_types import RolledUpItem
from app.graphql.submittals.strawberry.submittal_input import GenerateSubmittalPdfInput


class PdfTableService:
    def __init__(self) -> None:  # pyright: ignore[reportMissingSuperCall]
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self) -> None:
        self.styles.add(
            ParagraphStyle(
                name="TransmittalHeader",
                parent=self.styles["Heading2"],
                fontSize=16,
                spaceAfter=12,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="ItemDescription",
                parent=self.styles["Normal"],
                fontSize=10,
                leading=12,
            )
        )

    def generate_transmittal_page(
        self,
        submittal: Submittal,
        items: list[SubmittalItem | RolledUpItem],
        addressed_to: list[SubmittalStakeholder],
        input_data: GenerateSubmittalPdfInput,
    ) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=inch,
            bottomMargin=inch,
            leftMargin=inch,
            rightMargin=inch,
        )

        elements: list[Flowable] = []

        elements.append(Paragraph("TRANSMITTAL", self.styles["TransmittalHeader"]))
        elements.append(Spacer(1, 0.25 * inch))

        info_data = [
            ["Submittal #:", submittal.submittal_number],
            ["Date:", datetime.now().strftime("%B %d, %Y")],
            ["Number of Items:", str(len(items))],
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
        elements.append(info_table)
        elements.append(Spacer(1, 0.25 * inch))

        self._add_attached_section(elements, input_data)
        self._add_transmitted_for_section(elements, input_data)
        self._add_addressed_to_section(elements, addressed_to)

        elements.append(Paragraph("Items:", self.styles["TransmittalHeader"]))
        items_table = self._build_items_table(items, input_data, is_summary=False)
        elements.append(items_table)

        doc.build(elements)
        return buffer.getvalue()

    def generate_fixture_summary(
        self,
        submittal: Submittal,
        items: list[SubmittalItem | RolledUpItem],
        input_data: GenerateSubmittalPdfInput,
    ) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=inch,
            bottomMargin=inch,
            leftMargin=0.75 * inch,
            rightMargin=0.75 * inch,
        )

        elements: list[Flowable] = []

        elements.append(Paragraph("FIXTURE SUMMARY", self.styles["TransmittalHeader"]))
        elements.append(
            Paragraph(
                f"Submittal #: {submittal.submittal_number}",
                self.styles["Normal"],
            )
        )
        elements.append(Spacer(1, 0.25 * inch))

        summary_table = self._build_items_table(items, input_data, is_summary=True)
        elements.append(summary_table)

        doc.build(elements)
        return buffer.getvalue()

    def _add_attached_section(
        self, elements: list, input_data: GenerateSubmittalPdfInput
    ) -> None:
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

    def _add_transmitted_for_section(
        self, elements: list, input_data: GenerateSubmittalPdfInput
    ) -> None:
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

    def _add_addressed_to_section(
        self, elements: list, addressed_to: list[SubmittalStakeholder]
    ) -> None:
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

    def _build_items_table(
        self,
        items: list[SubmittalItem | RolledUpItem],
        input_data: GenerateSubmittalPdfInput,
        is_summary: bool,
    ) -> Table:
        if is_summary:
            return self._build_summary_table(items, input_data)
        return self._build_transmittal_table(items, input_data)

    def _build_transmittal_table(
        self,
        items: list[SubmittalItem | RolledUpItem],
        input_data: GenerateSubmittalPdfInput,
    ) -> Table:
        header = ["#", "Part Number", "Description"]
        if input_data.show_quantities:
            header.append("Qty")
        if input_data.show_lead_times:
            header.append("Lead Time")
        if not input_data.hide_notes:
            header.append("Notes")

        table_data = [header]
        for i, item in enumerate(items, 1):
            row = [
                str(i),
                item.part_number or "-",
                (item.description or "-")[:50],
            ]
            if input_data.show_quantities:
                row.append(str(item.quantity) if item.quantity else "-")
            if input_data.show_lead_times:
                row.append(item.lead_time or "-")
            if not input_data.hide_notes:
                notes = item.notes or "-"
                if len(notes) > 30:
                    notes = notes[:27] + "..."
                row.append(notes)
            table_data.append(row)

        col_widths = [0.4 * inch, 1.5 * inch, 2.5 * inch]
        if input_data.show_quantities:
            col_widths.append(0.6 * inch)
        if input_data.show_lead_times:
            col_widths.append(1.0 * inch)
        if not input_data.hide_notes:
            col_widths.append(1.2 * inch)

        items_table = Table(table_data, colWidths=col_widths)
        items_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("TOPPADDING", (0, 0), (-1, 0), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        return items_table

    def _build_summary_table(
        self,
        items: list[SubmittalItem | RolledUpItem],
        input_data: GenerateSubmittalPdfInput,
    ) -> Table:
        header = ["Item", "Part Number"]
        if input_data.show_descriptions:
            header.append("Description")
        if input_data.show_quantities:
            header.append("Qty")
        if input_data.show_lead_times:
            header.append("Lead Time")
        if not input_data.hide_notes:
            header.append("Notes")
        header.append("Status")

        table_data = [header]
        for i, item in enumerate(items, 1):
            row = [str(i), item.part_number or "-"]
            if input_data.show_descriptions:
                desc = item.description or "-"
                if len(desc) > 40:
                    desc = desc[:37] + "..."
                row.append(desc)
            if input_data.show_quantities:
                row.append(str(item.quantity) if item.quantity else "-")
            if input_data.show_lead_times:
                row.append(item.lead_time or "-")
            if not input_data.hide_notes:
                notes = item.notes or "-"
                if len(notes) > 30:
                    notes = notes[:27] + "..."
                row.append(notes)
            row.append(
                str(item.approval_status.value) if item.approval_status else "PENDING"
            )
            table_data.append(row)

        col_widths = [0.5 * inch, 1.3 * inch]
        if input_data.show_descriptions:
            col_widths.append(2.0 * inch)
        if input_data.show_quantities:
            col_widths.append(0.5 * inch)
        if input_data.show_lead_times:
            col_widths.append(1.0 * inch)
        if not input_data.hide_notes:
            col_widths.append(1.2 * inch)
        col_widths.append(1 * inch)

        summary_table = Table(table_data, colWidths=col_widths)
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                    ("TOPPADDING", (0, 0), (-1, 0), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ]
            )
        )
        return summary_table
