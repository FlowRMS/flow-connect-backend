import io
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from commons.db.v6.crm.submittals import Submittal, SubmittalItem
from loguru import logger
from pypdf import PdfReader, PdfWriter

from app.graphql.submittals.services.pdf_cover_page_service import PdfCoverPageService
from app.graphql.submittals.services.pdf_item_filter import (
    ACCESSORIES_KEYWORDS,
    CQ_KEYWORDS,
    KITS_KEYWORDS,
    LAMPS_KEYWORDS,
    apply_config_filters,
    get_item_category_title,
    is_item_from_order,
    matches_category,
)
from app.graphql.submittals.services.pdf_spec_sheet_service import PdfSpecSheetService
from app.graphql.submittals.services.pdf_table_service import PdfTableService
from app.graphql.submittals.services.pdf_types import PdfGenerationResult, RolledUpItem
from app.graphql.submittals.strawberry.submittal_input import GenerateSubmittalPdfInput

if TYPE_CHECKING:
    from app.graphql.submittals.services.submittal_pdf_export_service import (
        SpecSheetWithHighlights,
    )

# Re-export for backward compatibility
__all__ = [
    "ACCESSORIES_KEYWORDS",
    "CQ_KEYWORDS",
    "KITS_KEYWORDS",
    "LAMPS_KEYWORDS",
    "PdfGenerationResult",
    "PdfGenerationService",
    "RolledUpItem",
]


class PdfGenerationService:
    def __init__(self) -> None:  # pyright: ignore[reportMissingSuperCall]
        self.cover_service = PdfCoverPageService()
        self.table_service = PdfTableService()
        self.spec_sheet_service = PdfSpecSheetService()

    @staticmethod
    def _get_item_category_title(item: SubmittalItem) -> str | None:
        return get_item_category_title(item)

    @staticmethod
    def _matches_category(title: str | None, keywords: tuple[str, ...]) -> bool:
        return matches_category(title, keywords)

    @staticmethod
    def _is_item_from_order(item: SubmittalItem) -> bool:
        return is_item_from_order(item)

    async def generate_submittal_pdf(
        self,
        submittal: Submittal,
        input_data: GenerateSubmittalPdfInput,
        spec_sheet_data: dict[UUID, "SpecSheetWithHighlights"] | None = None,
        logo_bytes: bytes | None = None,
    ) -> PdfGenerationResult:
        try:
            logger.info(f"Generating PDF for submittal {submittal.id}")

            items_to_include = self._filter_items(submittal, input_data)
            self._apply_display_overrides(submittal, input_data)

            addressed_to = submittal.stakeholders
            if input_data.addressed_to_ids:
                addressed_ids_set = set(input_data.addressed_to_ids)
                addressed_to = [
                    s for s in submittal.stakeholders if s.id in addressed_ids_set
                ]

            pdf_writer = PdfWriter()

            if input_data.include_cover_page:
                cover_pdf = self.cover_service.generate_cover_page(
                    submittal, addressed_to, logo_bytes=logo_bytes
                )
                self._add_pdf_to_writer(pdf_writer, cover_pdf)

            if input_data.include_transmittal_page:
                transmittal_pdf = self.table_service.generate_transmittal_page(
                    submittal=submittal,
                    items=items_to_include,
                    addressed_to=addressed_to,
                    input_data=input_data,
                )
                self._add_pdf_to_writer(pdf_writer, transmittal_pdf)

            if input_data.include_fixture_summary:
                summary_pdf = self.table_service.generate_fixture_summary(
                    submittal=submittal,
                    items=items_to_include,
                    input_data=input_data,
                )
                self._add_pdf_to_writer(pdf_writer, summary_pdf)

            if input_data.include_pages and spec_sheet_data:
                self._add_spec_sheets(
                    pdf_writer, items_to_include, spec_sheet_data, input_data
                )

            if input_data.print_duplex:
                pdf_writer.add_metadata({"/Duplex": "/DuplexFlipLongEdge"})

            output_buffer = io.BytesIO()
            _ = pdf_writer.write(output_buffer)
            pdf_bytes = output_buffer.getvalue()

            if input_data.cap_file_size_mb and input_data.cap_file_size_mb > 0:
                max_bytes = input_data.cap_file_size_mb * 1024 * 1024
                if len(pdf_bytes) > max_bytes:
                    logger.warning(
                        f"PDF size {len(pdf_bytes)} exceeds cap {max_bytes} bytes"
                    )
                    pdf_bytes = self._cap_pdf_size(pdf_writer, max_bytes)

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
            return PdfGenerationResult(success=False, error=str(e))

    def _filter_items(
        self, submittal: Submittal, input_data: GenerateSubmittalPdfInput
    ) -> list[SubmittalItem | RolledUpItem]:
        items = list(submittal.items)
        if input_data.selected_item_ids:
            selected_ids_set = set(input_data.selected_item_ids)
            items = [item for item in items if item.id in selected_ids_set]

        if not submittal.config_include_zero_quantity_items:
            before_count = len(items)
            items = [
                item
                for item in items
                if item.quantity is not None and item.quantity != 0
            ]
            logger.info(f"Filtered zero-quantity items: {before_count} -> {len(items)}")

        return apply_config_filters(items, submittal)

    def _apply_display_overrides(
        self, submittal: Submittal, input_data: GenerateSubmittalPdfInput
    ) -> None:
        if submittal.config_drop_descriptions:
            input_data.show_descriptions = False
        if submittal.config_drop_line_notes:
            input_data.hide_notes = True

    def _add_spec_sheets(
        self,
        pdf_writer: PdfWriter,
        items: list[SubmittalItem | RolledUpItem],
        spec_sheet_data: dict[UUID, "SpecSheetWithHighlights"],
        input_data: GenerateSubmittalPdfInput,
    ) -> None:
        logger.info(
            f"Spec sheet attachment: include_pages={input_data.include_pages}, "
            f"spec_sheet_data={len(spec_sheet_data)}, items={len(items)}"
        )

        spec_sheets_added = 0
        current_manufacturer: str | None = None

        for item in items:
            if input_data.include_type_cover_page:
                manufacturer = item.manufacturer or "Unknown"
                if manufacturer != current_manufacturer:
                    current_manufacturer = manufacturer
                    type_cover = self.cover_service.generate_type_cover_page(
                        manufacturer
                    )
                    self._add_pdf_to_writer(pdf_writer, type_cover)

            if item.spec_sheet_id and item.spec_sheet_id in spec_sheet_data:
                data = spec_sheet_data[item.spec_sheet_id]
                if data.highlight_regions:
                    enhanced_pdf = self.spec_sheet_service.apply_highlights_to_pdf(
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
            f"Added {spec_sheets_added} spec sheet PDFs, "
            f"total pages: {len(pdf_writer.pages)}"
        )

    def _cap_pdf_size(self, writer: PdfWriter, max_bytes: int) -> bytes:
        while len(writer.pages) > 1:
            buf = io.BytesIO()
            _ = writer.write(buf)
            pdf_bytes = buf.getvalue()
            if len(pdf_bytes) <= max_bytes:
                return pdf_bytes
            writer.remove_page(len(writer.pages) - 1)

        buf = io.BytesIO()
        _ = writer.write(buf)
        return buf.getvalue()

    def _add_pdf_to_writer(self, writer: PdfWriter, pdf_bytes: bytes) -> None:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            _ = writer.add_page(page)
