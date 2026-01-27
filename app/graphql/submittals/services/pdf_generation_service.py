import io
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from commons.db.v6.crm.spec_sheets.spec_sheet_highlight_model import (
    SpecSheetHighlightRegion,
)
from commons.db.v6.crm.submittals import Submittal, SubmittalItem, SubmittalStakeholder
from commons.db.v6.crm.submittals.enums import SubmittalItemApprovalStatus
from loguru import logger
from pypdf import PdfReader, PdfWriter  # pyright: ignore[reportMissingImports]
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Image,
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

# Category title keywords used for matching (case-insensitive)
LAMPS_KEYWORDS = ("lamp", "lamps")
ACCESSORIES_KEYWORDS = ("accessor", "accessories", "accessory")
CQ_KEYWORDS = ("cq", "customer quoted")
KITS_KEYWORDS = ("kit", "kits")


@dataclass
class PdfGenerationResult:
    """Result of PDF generation."""

    success: bool
    pdf_bytes: bytes | None = None
    file_name: str | None = None
    file_size_bytes: int = 0
    error: str | None = None


@dataclass
class RolledUpItem:
    """A summary item representing rolled-up items of a category."""

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

    @staticmethod
    def _get_item_category_title(item: SubmittalItem) -> str | None:
        """Get the product category title from item's quote_detail chain."""
        try:
            qd = item.quote_detail
            if qd is None:
                return None
            product = qd.product
            if product is None:
                return None
            category = product.category
            if category is None:
                return None
            return category.title
        except Exception:
            return None

    @staticmethod
    def _matches_category(title: str | None, keywords: tuple[str, ...]) -> bool:
        """Check if a category title matches any of the given keywords (case-insensitive)."""
        if not title:
            return False
        lower = title.lower().strip()
        return any(kw in lower for kw in keywords)

    @staticmethod
    def _is_item_from_order(item: SubmittalItem) -> bool:
        """Check if an item originates from an order (quote_detail has order_id)."""
        try:
            qd = item.quote_detail
            if qd is None:
                return False
            return qd.order_id is not None
        except Exception:
            return False

    def _apply_config_filters(
        self,
        items: list[SubmittalItem],
        submittal: Submittal,
    ) -> list[SubmittalItem | RolledUpItem]:
        """Apply submittal config include/rollup filters to items list.

        Returns a list that may contain both SubmittalItem and RolledUpItem entries.
        """
        filtered = list(items)

        # --- Include filters: exclude items of certain categories when config is False ---
        if not submittal.config_include_lamps:
            before = len(filtered)
            filtered = [
                it
                for it in filtered
                if not self._matches_category(
                    self._get_item_category_title(it), LAMPS_KEYWORDS
                )
            ]
            if len(filtered) != before:
                logger.info(f"Excluded {before - len(filtered)} lamp items")

        if not submittal.config_include_accessories:
            before = len(filtered)
            filtered = [
                it
                for it in filtered
                if not self._matches_category(
                    self._get_item_category_title(it), ACCESSORIES_KEYWORDS
                )
            ]
            if len(filtered) != before:
                logger.info(f"Excluded {before - len(filtered)} accessory items")

        if not submittal.config_include_cq:
            before = len(filtered)
            filtered = [
                it
                for it in filtered
                if not self._matches_category(
                    self._get_item_category_title(it), CQ_KEYWORDS
                )
            ]
            if len(filtered) != before:
                logger.info(f"Excluded {before - len(filtered)} CQ items")

        if not submittal.config_include_from_orders:
            before = len(filtered)
            filtered = [it for it in filtered if not self._is_item_from_order(it)]
            if len(filtered) != before:
                logger.info(f"Excluded {before - len(filtered)} from-order items")

        # --- Rollup filters: consolidate items of certain categories ---
        result: list[SubmittalItem | RolledUpItem] = []
        rollup_kits: list[SubmittalItem] = []
        rollup_accessories: list[SubmittalItem] = []

        for it in filtered:
            cat_title = self._get_item_category_title(it)
            if submittal.config_roll_up_kits and self._matches_category(
                cat_title, KITS_KEYWORDS
            ):
                rollup_kits.append(it)
            elif submittal.config_roll_up_accessories and self._matches_category(
                cat_title, ACCESSORIES_KEYWORDS
            ):
                rollup_accessories.append(it)
            else:
                result.append(it)

        if rollup_kits:
            total_qty = sum((it.quantity or Decimal(0)) for it in rollup_kits)
            result.append(
                RolledUpItem(
                    part_number="(Kits - Rolled Up)",
                    description=f"{len(rollup_kits)} kit items consolidated",
                    quantity=total_qty if total_qty else None,
                    rolled_up_count=len(rollup_kits),
                )
            )
            logger.info(f"Rolled up {len(rollup_kits)} kit items into 1 summary row")

        if rollup_accessories:
            total_qty = sum((it.quantity or Decimal(0)) for it in rollup_accessories)
            result.append(
                RolledUpItem(
                    part_number="(Accessories - Rolled Up)",
                    description=f"{len(rollup_accessories)} accessory items consolidated",
                    quantity=total_qty if total_qty else None,
                    rolled_up_count=len(rollup_accessories),
                )
            )
            logger.info(
                f"Rolled up {len(rollup_accessories)} accessory items into 1 summary row"
            )

        return result

    async def generate_submittal_pdf(
        self,
        submittal: Submittal,
        input_data: GenerateSubmittalPdfInput,
        spec_sheet_data: dict[UUID, "SpecSheetWithHighlights"] | None = None,
        logo_bytes: bytes | None = None,
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
            items_to_include = list(submittal.items)
            if input_data.selected_item_ids:
                selected_ids_set = set(input_data.selected_item_ids)
                items_to_include = [
                    item for item in items_to_include if item.id in selected_ids_set
                ]

            # Apply submittal config: filter zero-quantity items
            if not submittal.config_include_zero_quantity_items:
                before_count = len(items_to_include)
                items_to_include = [
                    item
                    for item in items_to_include
                    if item.quantity is not None and item.quantity != 0
                ]
                logger.info(
                    f"Filtered zero-quantity items: {before_count} -> "
                    f"{len(items_to_include)}"
                )

            # Apply submittal config: include/exclude by category and rollup
            items_to_include = self._apply_config_filters(items_to_include, submittal)

            # Apply submittal config: override display options on input_data
            # so downstream methods (_generate_transmittal_page, etc.) respect them
            if submittal.config_drop_descriptions:
                input_data.show_descriptions = False
            if submittal.config_drop_line_notes:
                input_data.hide_notes = True

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
                cover_pdf = self._generate_cover_page(
                    submittal, addressed_to, logo_bytes=logo_bytes
                )
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
            logger.info(
                f"Spec sheet attachment: include_pages={input_data.include_pages}, "
                f"spec_sheet_data={'None' if spec_sheet_data is None else len(spec_sheet_data)}, "
                f"items_to_include={len(items_to_include)}"
            )
            if input_data.include_pages and spec_sheet_data:
                spec_sheets_added = 0
                # Group items by manufacturer for type cover pages
                if input_data.include_type_cover_page:
                    current_manufacturer: str | None = None
                    for item in items_to_include:
                        manufacturer = item.manufacturer or "Unknown"
                        if manufacturer != current_manufacturer:
                            current_manufacturer = manufacturer
                            type_cover = self._generate_type_cover_page(manufacturer)
                            self._add_pdf_to_writer(pdf_writer, type_cover)

                        if item.spec_sheet_id and item.spec_sheet_id in spec_sheet_data:
                            data = spec_sheet_data[item.spec_sheet_id]
                            if data.highlight_regions:
                                enhanced_pdf = self._apply_highlights_to_pdf(
                                    data.pdf_bytes, data.highlight_regions
                                )
                                self._add_pdf_to_writer(pdf_writer, enhanced_pdf)
                            else:
                                self._add_pdf_to_writer(pdf_writer, data.pdf_bytes)
                            spec_sheets_added += 1
                        else:
                            logger.info(
                                f"Item #{item.item_number}: spec_sheet_id={item.spec_sheet_id}, "
                                f"in_data={item.spec_sheet_id in spec_sheet_data if item.spec_sheet_id else 'N/A'}"
                            )
                else:
                    for item in items_to_include:
                        if item.spec_sheet_id and item.spec_sheet_id in spec_sheet_data:
                            data = spec_sheet_data[item.spec_sheet_id]
                            if data.highlight_regions:
                                enhanced_pdf = self._apply_highlights_to_pdf(
                                    data.pdf_bytes, data.highlight_regions
                                )
                                self._add_pdf_to_writer(pdf_writer, enhanced_pdf)
                            else:
                                self._add_pdf_to_writer(pdf_writer, data.pdf_bytes)
                            spec_sheets_added += 1
                        else:
                            logger.info(
                                f"Item #{item.item_number}: spec_sheet_id={item.spec_sheet_id}, "
                                f"in_data={item.spec_sheet_id in spec_sheet_data if item.spec_sheet_id else 'N/A'}"
                            )
                logger.info(
                    f"Added {spec_sheets_added} spec sheet PDFs to submittal, "
                    f"total pages so far: {len(pdf_writer.pages)}"
                )
            else:
                logger.warning(
                    f"Spec sheets NOT added: include_pages={input_data.include_pages}, "
                    f"spec_sheet_data={'None' if spec_sheet_data is None else len(spec_sheet_data)}"
                )

            # Set duplex printing preference if requested
            if input_data.print_duplex:
                pdf_writer.add_metadata({"/Duplex": "/DuplexFlipLongEdge"})

            # Write final PDF to bytes
            output_buffer = io.BytesIO()
            _ = pdf_writer.write(output_buffer)
            pdf_bytes = output_buffer.getvalue()

            # Cap file size if requested by removing trailing spec sheet pages
            if input_data.cap_file_size_mb and input_data.cap_file_size_mb > 0:
                max_bytes = input_data.cap_file_size_mb * 1024 * 1024
                if len(pdf_bytes) > max_bytes:
                    logger.warning(
                        f"PDF size {len(pdf_bytes)} exceeds cap "
                        f"{max_bytes} bytes, removing pages to fit"
                    )
                    pdf_bytes = self._cap_pdf_size(pdf_writer, max_bytes)

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

    def _cap_pdf_size(self, writer: PdfWriter, max_bytes: int) -> bytes:
        """Remove trailing pages until the PDF fits within max_bytes."""
        while len(writer.pages) > 1:
            buf = io.BytesIO()
            _ = writer.write(buf)
            pdf_bytes = buf.getvalue()
            if len(pdf_bytes) <= max_bytes:
                return pdf_bytes
            # Remove last page and try again
            writer.remove_page(len(writer.pages) - 1)

        # Even a single page; return whatever we have
        buf = io.BytesIO()
        _ = writer.write(buf)
        return buf.getvalue()

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
        logo_bytes: bytes | None = None,
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

        # Logo (centered, max 2 inches wide)
        if logo_bytes:
            try:
                logo_reader = ImageReader(io.BytesIO(logo_bytes))
                img_w, img_h = logo_reader.getSize()
                max_width = 2 * inch
                max_height = 1 * inch
                scale = min(max_width / img_w, max_height / img_h)
                elements.append(
                    Image(
                        io.BytesIO(logo_bytes),
                        width=img_w * scale,
                        height=img_h * scale,
                        hAlign="CENTER",
                    )
                )
                elements.append(Spacer(1, 0.3 * inch))
            except Exception as e:
                logger.warning(f"Failed to render logo on cover page: {e}")

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

    def _generate_type_cover_page(self, manufacturer: str) -> bytes:
        """Generate a separator cover page for a manufacturer/type group."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=3 * inch,
            bottomMargin=inch,
            leftMargin=inch,
            rightMargin=inch,
        )

        elements: list[Any] = []
        elements.append(Paragraph(manufacturer.upper(), self.styles["CoverTitle"]))

        doc.build(elements)
        return buffer.getvalue()

    def _generate_transmittal_page(
        self,
        submittal: Submittal,
        items: list[SubmittalItem | RolledUpItem],
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

        # Transmitted for section
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
        if input_data.show_lead_times:
            header.append("Lead Time")
        if not input_data.hide_notes:
            header.append("Notes")

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
            if input_data.show_lead_times:
                row.append(item.lead_time or "-")
            if not input_data.hide_notes:
                notes = item.notes or "-"
                if len(notes) > 30:
                    notes = notes[:27] + "..."
                row.append(notes)
            table_data.append(row)

        # Calculate column widths
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
        elements.append(items_table)

        doc.build(elements)
        return buffer.getvalue()

    def _generate_fixture_summary(
        self,
        submittal: Submittal,
        items: list[SubmittalItem | RolledUpItem],
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
        if input_data.show_lead_times:
            header.append("Lead Time")
        if not input_data.hide_notes:
            header.append("Notes")
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

        # Calculate column widths based on included columns
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
                    ("ALIGN", (0, 0), (0, -1), "CENTER"),  # Item column centered
                ]
            )
        )
        elements.append(summary_table)

        doc.build(elements)
        return buffer.getvalue()
