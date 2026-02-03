import io
from datetime import datetime
from typing import TYPE_CHECKING

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer

if TYPE_CHECKING:
    from reportlab.platypus.flowables import Flowable

from commons.db.v6.crm.submittals import Submittal, SubmittalStakeholder
from loguru import logger


class PdfCoverPageService:
    def __init__(self) -> None:  # pyright: ignore[reportMissingSuperCall]
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self) -> None:
        self.styles.add(
            ParagraphStyle(
                name="CoverTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                spaceAfter=30,
                alignment=1,
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

    def generate_cover_page(
        self,
        submittal: Submittal,
        addressed_to: list[SubmittalStakeholder],
        logo_bytes: bytes | None = None,
    ) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=1.5 * inch,
            bottomMargin=inch,
            leftMargin=inch,
            rightMargin=inch,
        )

        elements: list[Flowable] = []

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

        elements.append(Paragraph("SUBMITTAL", self.styles["CoverTitle"]))
        elements.append(Spacer(1, 0.5 * inch))

        elements.append(
            Paragraph(
                f"Submittal #: {submittal.submittal_number}",
                self.styles["CoverSubtitle"],
            )
        )

        if submittal.description:
            elements.append(
                Paragraph(submittal.description, self.styles["CoverSubtitle"])
            )

        elements.append(Spacer(1, inch))

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

        elements.append(
            Paragraph(
                f"Date: {datetime.now().strftime('%B %d, %Y')}",
                self.styles["Normal"],
            )
        )

        doc.build(elements)
        return buffer.getvalue()

    def generate_type_cover_page(self, manufacturer: str) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=3 * inch,
            bottomMargin=inch,
            leftMargin=inch,
            rightMargin=inch,
        )

        elements: list[Flowable] = []
        elements.append(Paragraph(manufacturer.upper(), self.styles["CoverTitle"]))

        doc.build(elements)
        return buffer.getvalue()
