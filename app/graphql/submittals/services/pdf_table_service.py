import io
from typing import TYPE_CHECKING

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

if TYPE_CHECKING:
    from reportlab.platypus.flowables import Flowable

from commons.db.v6.crm.submittals import Submittal, SubmittalItem, SubmittalStakeholder

from app.graphql.submittals.services.pdf_transmittal_service import (
    PdfTransmittalService,
)
from app.graphql.submittals.services.pdf_types import RolledUpItem
from app.graphql.submittals.strawberry.generate_submittal_pdf_input import (
    GenerateSubmittalPdfInput,
)


class PdfTableService:
    def __init__(self) -> None:  # pyright: ignore[reportMissingSuperCall]
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self._transmittal_service = PdfTransmittalService(self.styles)

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

        info_table = self._transmittal_service.build_info_table(
            submittal, len(items), input_data
        )
        elements.append(info_table)
        elements.append(Spacer(1, 0.25 * inch))

        self._transmittal_service.add_attached_section(elements, input_data)
        self._transmittal_service.add_transmitted_for_section(elements, input_data)
        self._transmittal_service.add_addressed_to_section(elements, addressed_to)

        elements.append(Paragraph("Items:", self.styles["TransmittalHeader"]))
        items_table = self._build_transmittal_table(items, input_data)
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

        summary_table = self._build_summary_table(items, input_data)
        elements.append(summary_table)

        doc.build(elements)
        return buffer.getvalue()

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
