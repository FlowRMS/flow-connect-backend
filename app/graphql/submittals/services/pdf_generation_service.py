import io
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from commons.db.v6.crm.spec_sheets.spec_sheet_highlight_model import (
    SpecSheetHighlightRegion,
)
from commons.db.v6.crm.submittals import Submittal, SubmittalItem, SubmittalStakeholder
from loguru import logger
from pypdf import PdfReader, PdfWriter  # pyright: ignore[reportMissingImports]
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    PageBreak,  # pyright: ignore[reportUnusedImport]
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.graphql.submittals.strawberry.submittal_input import GenerateSubmittalPdfInput

if TYPE_CHECKING:
    from app.graphql.submittals.services.submittal_pdf_export_service import (
        SpecSheetWithHighlights,
    )


@dataclass
class PdfGenerationResult:
    """Result of PDF generation."""

    success: bool
    pdf_bytes: bytes | None = None
    file_name: str | None = None
    file_size_bytes: int = 0
    error: str | None = None


class PdfGenerationService:
    """Service for generating submittal PDFs using ReportLab."""

    def __init__(self) -> None:  # pyright: ignore[reportMissingSuperCall]
        """Initialize PDF generation service."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self) -> None:
        """Set up custom paragraph styles."""
        self.styles.add(
            ParagraphStyle(
                name="CoverTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                spaceAfter=30,
                alignment=1,  # Center
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="CoverSubtitle",
                parent=self.styles["Normal"],
                fontSize=14,
                spaceAfter=20,
                alignment=1,
            )
        )
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

    async def generate_submittal_pdf(
        self,
        submittal: Submittal,
        input_data: GenerateSubmittalPdfInput,
        spec_sheet_data: dict[UUID, "SpecSheetWithHighlights"] | None = None,
    ) -> PdfGenerationResult:
        """
        Generate a complete submittal PDF package.

        Args:
            submittal: The submittal to generate PDF for
            input_data: Generation options
            spec_sheet_data: Dict mapping spec sheet IDs to their PDF bytes and highlights

        Returns:
            PdfGenerationResult with PDF bytes and metadata
        """
        try:
            logger.info(f"Generating PDF for submittal {submittal.id}")

            # Filter items if specific ones are selected
            items_to_include = submittal.items
            if input_data.selected_item_ids:
                selected_ids_set = set(input_data.selected_item_ids)
                items_to_include = [
                    item for item in submittal.items if item.id in selected_ids_set
                ]

            # Filter stakeholders if specific ones are selected
            addressed_to = submittal.stakeholders
            if input_data.addressed_to_ids:
                addressed_ids_set = set(input_data.addressed_to_ids)
                addressed_to = [
                    s for s in submittal.stakeholders if s.id in addressed_ids_set
                ]

            # Create PDF writer to combine all pages
            pdf_writer = PdfWriter()

            # Generate cover page
            if input_data.include_cover_page:
                cover_pdf = self._generate_cover_page(submittal, addressed_to)
                self._add_pdf_to_writer(pdf_writer, cover_pdf)

            # Generate transmittal page
            if input_data.include_transmittal_page:
                transmittal_pdf = self._generate_transmittal_page(
                    submittal=submittal,
                    items=items_to_include,
                    addressed_to=addressed_to,
                    input_data=input_data,
                )
                self._add_pdf_to_writer(pdf_writer, transmittal_pdf)

            # Generate fixture summary
            if input_data.include_fixture_summary:
                summary_pdf = self._generate_fixture_summary(
                    submittal=submittal,
                    items=items_to_include,
                    input_data=input_data,
                )
                self._add_pdf_to_writer(pdf_writer, summary_pdf)

            # Add spec sheet pages with highlights
            if input_data.include_pages and spec_sheet_data:
                for item in items_to_include:
                    if item.spec_sheet_id and item.spec_sheet_id in spec_sheet_data:
                        data = spec_sheet_data[item.spec_sheet_id]
                        # Apply highlights if any
                        if data.highlight_regions:
                            enhanced_pdf = self._apply_highlights_to_pdf(
                                data.pdf_bytes, data.highlight_regions
                            )
                            self._add_pdf_to_writer(pdf_writer, enhanced_pdf)
                        else:
                            self._add_pdf_to_writer(pdf_writer, data.pdf_bytes)

            # Write final PDF to bytes
            output_buffer = io.BytesIO()
            _ = pdf_writer.write(output_buffer)
            pdf_bytes = output_buffer.getvalue()

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"Submittal_{submittal.submittal_number}_{timestamp}.pdf"

            logger.info(
                f"Generated PDF for submittal {submittal.id}: "
                f"{len(pdf_bytes)} bytes, {len(pdf_writer.pages)} pages"
            )

            return PdfGenerationResult(
                success=True,
                pdf_bytes=pdf_bytes,
                file_name=file_name,
                file_size_bytes=len(pdf_bytes),
            )

        except Exception as e:
            logger.error(f"Failed to generate PDF for submittal {submittal.id}: {e}")
            return PdfGenerationResult(
                success=False,
                error=str(e),
            )

    def _add_pdf_to_writer(self, writer: PdfWriter, pdf_bytes: bytes) -> None:
        """Add PDF bytes to the writer."""
        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            _ = writer.add_page(page)

    def _apply_highlights_to_pdf(
        self,
        pdf_bytes: bytes,
        regions: list[SpecSheetHighlightRegion],
    ) -> bytes:
        """
        Apply highlight regions as overlays on PDF pages.

        Args:
            pdf_bytes: Original PDF bytes
            regions: List of highlight regions with coordinates in percentages

        Returns:
            PDF bytes with highlights applied
        """
        reader = PdfReader(io.BytesIO(pdf_bytes))
        writer = PdfWriter()

        # Group regions by page number (1-indexed in model)
        regions_by_page: dict[int, list[SpecSheetHighlightRegion]] = {}
        for region in regions:
            page_num = region.page_number
            if page_num not in regions_by_page:
                regions_by_page[page_num] = []
            regions_by_page[page_num].append(region)

        for page_index, page in enumerate(reader.pages):
            page_num = page_index + 1  # Convert to 1-indexed
            page_regions = regions_by_page.get(page_num, [])

            if page_regions:
                # Get page dimensions
                media_box = page.mediabox
                page_width = float(media_box.width)
                page_height = float(media_box.height)

                # Create overlay canvas
                overlay_buffer = io.BytesIO()
                c = canvas.Canvas(overlay_buffer, pagesize=(page_width, page_height))

                for region in page_regions:
                    self._draw_highlight_region(c, region, page_width, page_height)

                c.save()
                _ = overlay_buffer.seek(0)

                # Merge overlay onto page
                overlay_reader = PdfReader(overlay_buffer)
                if overlay_reader.pages:
                    page.merge_page(overlay_reader.pages[0])

            _ = writer.add_page(page)

        output_buffer = io.BytesIO()
        _ = writer.write(output_buffer)
        return output_buffer.getvalue()

    def _draw_highlight_region(
        self,
        c: canvas.Canvas,
        region: SpecSheetHighlightRegion,
        page_width: float,
        page_height: float,
    ) -> None:
        """
        Draw a single highlight region on the canvas.

        Args:
            c: ReportLab canvas
            region: Highlight region with percentage coordinates
            page_width: PDF page width in points
            page_height: PDF page height in points
        """
        # Convert percentage coordinates to absolute
        # Note: PDF coordinates are from bottom-left, region y is from top
        x = (region.x / 100.0) * page_width
        y_from_top = (region.y / 100.0) * page_height
        width = (region.width / 100.0) * page_width
        height = (region.height / 100.0) * page_height

        # Convert y from top-origin to bottom-origin
        y = page_height - y_from_top - height

        # Parse hex color and set with alpha for transparency
        hex_color = region.color.lstrip("#")
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0

        # Set stroke and fill colors with transparency
        c.setStrokeColorRGB(r, g, b)
        c.setFillColorRGB(r, g, b, alpha=0.3)  # Semi-transparent fill
        c.setLineWidth(2)

        if region.shape_type == "oval":
            # Draw oval (ellipse)
            c.ellipse(x, y, x + width, y + height, stroke=1, fill=1)
        else:
            # Draw rectangle (default for 'rectangle' and 'highlight')
            c.rect(x, y, width, height, stroke=1, fill=1)

    def _generate_cover_page(
        self,
        submittal: Submittal,
        addressed_to: list[SubmittalStakeholder],
    ) -> bytes:
        """Generate the cover page PDF."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=1.5 * inch,
            bottomMargin=inch,
            leftMargin=inch,
            rightMargin=inch,
        )

        elements: list[Any] = []

        # Title
        elements.append(Paragraph("SUBMITTAL", self.styles["CoverTitle"]))
        elements.append(Spacer(1, 0.5 * inch))

        # Submittal number
        elements.append(
            Paragraph(
                f"Submittal #: {submittal.submittal_number}",
                self.styles["CoverSubtitle"],
            )
        )

        # Description if available
        if submittal.description:
            elements.append(
                Paragraph(submittal.description, self.styles["CoverSubtitle"])
            )

        elements.append(Spacer(1, inch))

        # Addressed to section
        if addressed_to:
            elements.append(
                Paragraph("Addressed To:", self.styles["TransmittalHeader"])
            )
            for stakeholder in addressed_to:
                name = stakeholder.contact_name or "Unknown"
                company = stakeholder.company_name or ""
                role = stakeholder.role.value if stakeholder.role else ""
                text = f"{name}"
                if company:
                    text += f" - {company}"
                if role:
                    text += f" ({role})"
                elements.append(Paragraph(text, self.styles["Normal"]))
            elements.append(Spacer(1, 0.5 * inch))

        # Date
        elements.append(
            Paragraph(
                f"Date: {datetime.now().strftime('%B %d, %Y')}",
                self.styles["Normal"],
            )
        )

        doc.build(elements)
        return buffer.getvalue()

    def _generate_transmittal_page(
        self,
        submittal: Submittal,
        items: list[SubmittalItem],
        addressed_to: list[SubmittalStakeholder],
        input_data: GenerateSubmittalPdfInput,
    ) -> bytes:
        """Generate the transmittal page PDF."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=inch,
            bottomMargin=inch,
            leftMargin=inch,
            rightMargin=inch,
        )

        elements: list[Any] = []

        # Header
        elements.append(Paragraph("TRANSMITTAL", self.styles["TransmittalHeader"]))
        elements.append(Spacer(1, 0.25 * inch))

        # Submittal info
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

        # Attached items section
        if input_data.attached_items:
            elements.append(Paragraph("Attached:", self.styles["Normal"]))
            attached_text = ", ".join(input_data.attached_items)
            if input_data.attached_other:
                attached_text += f", {input_data.attached_other}"
            elements.append(Paragraph(attached_text, self.styles["ItemDescription"]))
            elements.append(Spacer(1, 0.15 * inch))

        # Transmitted for section
        if input_data.transmitted_for:
            elements.append(Paragraph("Transmitted For:", self.styles["Normal"]))
            transmitted_text = ", ".join(input_data.transmitted_for)
            if input_data.transmitted_for_other:
                transmitted_text += f", {input_data.transmitted_for_other}"
            elements.append(Paragraph(transmitted_text, self.styles["ItemDescription"]))
            elements.append(Spacer(1, 0.15 * inch))

        # Addressed to
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

        # Items table
        elements.append(Paragraph("Items:", self.styles["TransmittalHeader"]))

        # Build table header
        header = ["#", "Part Number", "Description"]
        if input_data.show_quantities:
            header.append("Qty")

        # Build table data
        table_data = [header]
        for i, item in enumerate(items, 1):
            row = [
                str(i),
                item.part_number or "-",
                (item.description or "-")[:50],  # Truncate long descriptions
            ]
            if input_data.show_quantities:
                row.append(str(item.quantity) if item.quantity else "-")
            table_data.append(row)

        # Calculate column widths
        col_widths = [0.4 * inch, 1.5 * inch, 3.5 * inch]
        if input_data.show_quantities:
            col_widths.append(0.6 * inch)

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
        elements.append(items_table)

        doc.build(elements)
        return buffer.getvalue()

    def _generate_fixture_summary(
        self,
        submittal: Submittal,
        items: list[SubmittalItem],
        input_data: GenerateSubmittalPdfInput,
    ) -> bytes:
        """Generate the fixture summary page PDF."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=inch,
            bottomMargin=inch,
            leftMargin=0.75 * inch,
            rightMargin=0.75 * inch,
        )

        elements: list[Any] = []

        # Header
        elements.append(Paragraph("FIXTURE SUMMARY", self.styles["TransmittalHeader"]))
        elements.append(
            Paragraph(
                f"Submittal #: {submittal.submittal_number}",
                self.styles["Normal"],
            )
        )
        elements.append(Spacer(1, 0.25 * inch))

        # Build table header
        header = ["Item", "Part Number"]
        if input_data.show_descriptions:
            header.append("Description")
        if input_data.show_quantities:
            header.append("Qty")
        header.append("Status")

        # Build table data
        table_data = [header]
        for i, item in enumerate(items, 1):
            row = [
                str(i),
                item.part_number or "-",
            ]
            if input_data.show_descriptions:
                desc = item.description or "-"
                if len(desc) > 40:
                    desc = desc[:37] + "..."
                row.append(desc)
            if input_data.show_quantities:
                row.append(str(item.quantity) if item.quantity else "-")
            row.append(
                str(item.approval_status.value) if item.approval_status else "PENDING"
            )
            table_data.append(row)

        # Calculate column widths based on included columns
        col_widths = [0.5 * inch, 1.3 * inch]
        if input_data.show_descriptions:
            col_widths.append(2.5 * inch)
        if input_data.show_quantities:
            col_widths.append(0.5 * inch)
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
                    ("ALIGN", (0, 0), (0, -1), "CENTER"),  # Item column centered
                ]
            )
        )
        elements.append(summary_table)

        doc.build(elements)
        return buffer.getvalue()
