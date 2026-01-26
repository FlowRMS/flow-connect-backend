import io
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from commons.db.v6.crm.spec_sheets.spec_sheet_highlight_model import (
    SpecSheetHighlightRegion,
)
from commons.db.v6.crm.spec_sheets.spec_sheet_model import SpecSheet
from commons.db.v6.crm.submittals import Submittal
from commons.s3.service import S3Service
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.submittals.services.pdf_generation_service import (
    PdfGenerationService,
)
from app.graphql.submittals.strawberry.submittal_input import GenerateSubmittalPdfInput

SUBMITTAL_PDFS_S3_PREFIX = "submittal-pdfs"


@dataclass
class SpecSheetWithHighlights:
    """Spec sheet PDF bytes with associated highlight regions."""

    pdf_bytes: bytes
    highlight_regions: list[SpecSheetHighlightRegion] = field(default_factory=list)


@dataclass
class SubmittalPdfExportResult:
    success: bool
    pdf_url: str | None = None
    pdf_file_name: str | None = None
    pdf_file_size_bytes: int = 0
    error: str | None = None


class SubmittalPdfExportService:
    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        s3_service: S3Service,
        session: AsyncSession,
    ) -> None:
        self.s3_service = s3_service
        self.session = session
        self.pdf_service = PdfGenerationService()

    async def export_submittal_pdf(
        self,
        submittal: Submittal,
        input_data: GenerateSubmittalPdfInput,
    ) -> SubmittalPdfExportResult:
        try:
            spec_sheet_data = await self._fetch_spec_sheet_pdfs_with_highlights(
                submittal, input_data
            )

            pdf_result = await self.pdf_service.generate_submittal_pdf(
                submittal=submittal,
                input_data=input_data,
                spec_sheet_data=spec_sheet_data,
            )

            if not pdf_result.success:
                return SubmittalPdfExportResult(
                    success=False,
                    error=pdf_result.error,
                )

            s3_url = await self._upload_pdf_to_s3(
                pdf_bytes=pdf_result.pdf_bytes or b"",
                file_name=pdf_result.file_name
                or f"Submittal_{submittal.submittal_number}.pdf",
                submittal_id=submittal.id,
            )

            logger.info(
                f"Exported submittal PDF {submittal.id}: "
                f"{pdf_result.file_size_bytes} bytes, "
                f"{len(spec_sheet_data)} spec sheets included"
            )

            return SubmittalPdfExportResult(
                success=True,
                pdf_url=s3_url,
                pdf_file_name=pdf_result.file_name,
                pdf_file_size_bytes=pdf_result.file_size_bytes,
            )

        except Exception as e:
            logger.error(f"Failed to export submittal PDF {submittal.id}: {e}")
            return SubmittalPdfExportResult(
                success=False,
                error=str(e),
            )

    async def _fetch_spec_sheet_pdfs_with_highlights(
        self,
        submittal: Submittal,
        input_data: GenerateSubmittalPdfInput,
    ) -> dict[UUID, SpecSheetWithHighlights]:
        """Fetch spec sheet PDFs with their associated highlight regions."""
        if not input_data.include_pages:
            return {}

        items = submittal.items
        if input_data.selected_item_ids:
            selected_ids = set(input_data.selected_item_ids)
            items = [item for item in items if item.id in selected_ids]

        # Build mapping of spec_sheet_id -> highlight_regions
        spec_sheet_highlights: dict[UUID, list[SpecSheetHighlightRegion]] = {}
        spec_sheet_ids: list[UUID] = []

        for item in items:
            if item.spec_sheet_id is not None:
                spec_sheet_ids.append(item.spec_sheet_id)
                # Get highlight regions if highlight_version is loaded
                if (
                    item.highlight_version is not None
                    and item.highlight_version.regions
                ):
                    spec_sheet_highlights[item.spec_sheet_id] = list(
                        item.highlight_version.regions
                    )

        if not spec_sheet_ids:
            logger.debug("No spec sheets linked to submittal items")
            return {}

        spec_sheets = await self._get_spec_sheets_by_ids(spec_sheet_ids)

        result: dict[UUID, SpecSheetWithHighlights] = {}
        for spec_sheet in spec_sheets:
            pdf_bytes = await self._download_spec_sheet_pdf(spec_sheet)
            if pdf_bytes:
                result[spec_sheet.id] = SpecSheetWithHighlights(
                    pdf_bytes=pdf_bytes,
                    highlight_regions=spec_sheet_highlights.get(spec_sheet.id, []),
                )

        highlights_count = sum(len(data.highlight_regions) for data in result.values())
        logger.info(
            f"Fetched {len(result)}/{len(spec_sheet_ids)} spec sheet PDFs "
            f"with {highlights_count} highlight regions"
        )
        return result

    async def _get_spec_sheets_by_ids(self, ids: list[UUID]) -> list[SpecSheet]:
        stmt = select(SpecSheet).where(SpecSheet.id.in_(ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def _download_spec_sheet_pdf(self, spec_sheet: SpecSheet) -> bytes | None:
        try:
            s3_key = None
            if spec_sheet.file_url:
                url_info = S3Service.extract_url_info(spec_sheet.file_url)
                s3_key = url_info.key

            if not s3_key:
                logger.warning(f"No S3 key found for spec sheet {spec_sheet.id}")
                return None

            file_obj = await self.s3_service.download(key=s3_key)
            return file_obj.read()

        except Exception as e:
            logger.warning(f"Failed to download spec sheet PDF {spec_sheet.id}: {e}")
            return None

    async def _upload_pdf_to_s3(
        self,
        pdf_bytes: bytes,
        file_name: str,
        submittal_id: UUID,
    ) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        s3_key = f"{SUBMITTAL_PDFS_S3_PREFIX}/{submittal_id}/{timestamp}_{file_name}"

        await self.s3_service.upload(
            key=s3_key,
            file_obj=io.BytesIO(pdf_bytes),
            ContentType="application/pdf",
        )

        presigned_url = await self.s3_service.generate_presigned_url(key=s3_key)

        logger.info(f"Uploaded submittal PDF to S3: {s3_key}")
        return presigned_url
