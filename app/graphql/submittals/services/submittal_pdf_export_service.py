import io
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from commons.db.v6.crm.organizations.organization_model import Organization
from commons.db.v6.crm.spec_sheets.spec_sheet_highlight_model import (
    SpecSheetHighlightRegion,
)
from commons.db.v6.crm.spec_sheets.spec_sheet_model import SpecSheet
from commons.db.v6.crm.submittals import Submittal
from commons.db.v6.files import File
from commons.s3.service import S3Service
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.submittals.services.pdf_generation_service import (
    ACCESSORIES_KEYWORDS,
    CQ_KEYWORDS,
    KITS_KEYWORDS,
    LAMPS_KEYWORDS,
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

            # Fetch organization logo if requested
            logo_bytes: bytes | None = None
            if input_data.use_customer_logo:
                logo_bytes = await self._fetch_organization_logo()

            pdf_result = await self.pdf_service.generate_submittal_pdf(
                submittal=submittal,
                input_data=input_data,
                spec_sheet_data=spec_sheet_data,
                logo_bytes=logo_bytes,
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
            logger.info("include_pages is False, skipping spec sheet fetching")
            return {}

        items = list(submittal.items)
        logger.info(f"Submittal {submittal.id} has {len(items)} items total")
        if input_data.selected_item_ids:
            selected_ids = set(input_data.selected_item_ids)
            items = [item for item in items if item.id in selected_ids]
            logger.info(
                f"Filtered to {len(items)} items from "
                f"{len(input_data.selected_item_ids)} selected IDs"
            )

        # Apply submittal config: filter zero-quantity items
        if not submittal.config_include_zero_quantity_items:
            items = [
                item
                for item in items
                if item.quantity is not None and item.quantity != 0
            ]
            logger.info(f"After zero-quantity filter: {len(items)} items")

        # Apply submittal config: category/order include filters
        # (must match the same logic in PdfGenerationService._apply_config_filters)
        if not submittal.config_include_lamps:
            items = [
                it
                for it in items
                if not PdfGenerationService._matches_category(
                    PdfGenerationService._get_item_category_title(it), LAMPS_KEYWORDS
                )
            ]
        if not submittal.config_include_accessories:
            items = [
                it
                for it in items
                if not PdfGenerationService._matches_category(
                    PdfGenerationService._get_item_category_title(it),
                    ACCESSORIES_KEYWORDS,
                )
            ]
        if not submittal.config_include_cq:
            items = [
                it
                for it in items
                if not PdfGenerationService._matches_category(
                    PdfGenerationService._get_item_category_title(it), CQ_KEYWORDS
                )
            ]
        if not submittal.config_include_from_orders:
            items = [
                it for it in items if not PdfGenerationService._is_item_from_order(it)
            ]
        # Skip spec sheets for items that would be rolled up
        if submittal.config_roll_up_kits:
            items = [
                it
                for it in items
                if not PdfGenerationService._matches_category(
                    PdfGenerationService._get_item_category_title(it), KITS_KEYWORDS
                )
            ]
        if submittal.config_roll_up_accessories:
            items = [
                it
                for it in items
                if not PdfGenerationService._matches_category(
                    PdfGenerationService._get_item_category_title(it),
                    ACCESSORIES_KEYWORDS,
                )
            ]
        logger.info(f"After config include/rollup filters: {len(items)} items")

        # Build mapping of spec_sheet_id -> highlight_regions
        # Use the already-loaded spec_sheet relationship when available
        spec_sheet_highlights: dict[UUID, list[SpecSheetHighlightRegion]] = {}
        spec_sheets_from_items: dict[UUID, SpecSheet] = {}

        for item in items:
            if item.spec_sheet_id is not None:
                # Use the eagerly-loaded spec_sheet relationship directly
                if item.spec_sheet is not None:
                    spec_sheets_from_items[item.spec_sheet_id] = item.spec_sheet
                    logger.info(
                        f"Item {item.id} (#{item.item_number}): "
                        f"spec_sheet_id={item.spec_sheet_id}, "
                        f"file_url={item.spec_sheet.file_url[:80] if item.spec_sheet.file_url else 'None'}..."
                    )
                else:
                    logger.warning(
                        f"Item {item.id} (#{item.item_number}): "
                        f"spec_sheet_id={item.spec_sheet_id} set but "
                        f"spec_sheet relationship is None"
                    )

                # Get highlight regions if highlight_version is loaded
                if (
                    item.highlight_version is not None
                    and item.highlight_version.regions
                ):
                    spec_sheet_highlights[item.spec_sheet_id] = list(
                        item.highlight_version.regions
                    )
                    logger.info(
                        f"Item {item.id}: {len(item.highlight_version.regions)} "
                        f"highlight regions found"
                    )
            else:
                logger.info(f"Item {item.id} (#{item.item_number}): no spec_sheet_id")

        if not spec_sheets_from_items:
            # Fallback: try querying directly if relationships weren't loaded
            spec_sheet_ids = [
                item.spec_sheet_id for item in items if item.spec_sheet_id is not None
            ]
            if spec_sheet_ids:
                logger.info(
                    f"No spec sheets from relationships, "
                    f"querying DB for {len(spec_sheet_ids)} spec sheet IDs"
                )
                queried = await self._get_spec_sheets_by_ids(spec_sheet_ids)
                for ss in queried:
                    spec_sheets_from_items[ss.id] = ss
                logger.info(f"DB query returned {len(queried)} spec sheets")
            else:
                logger.info("No spec sheets linked to submittal items")
                return {}

        logger.info(f"Found {len(spec_sheets_from_items)} unique spec sheets to attach")

        result: dict[UUID, SpecSheetWithHighlights] = {}
        for ss_id, spec_sheet in spec_sheets_from_items.items():
            pdf_bytes = await self._download_spec_sheet_pdf(spec_sheet)
            if pdf_bytes:
                result[ss_id] = SpecSheetWithHighlights(
                    pdf_bytes=pdf_bytes,
                    highlight_regions=spec_sheet_highlights.get(ss_id, []),
                )
                logger.info(
                    f"Downloaded spec sheet {ss_id}: "
                    f"{len(pdf_bytes)} bytes, "
                    f"{len(spec_sheet_highlights.get(ss_id, []))} highlights"
                )
            else:
                logger.error(
                    f"Failed to download spec sheet PDF for {ss_id} "
                    f"(file_url={spec_sheet.file_url[:80] if spec_sheet.file_url else 'None'})"
                )

        highlights_count = sum(len(data.highlight_regions) for data in result.values())
        logger.info(
            f"Fetched {len(result)}/{len(spec_sheets_from_items)} spec sheet PDFs "
            f"with {highlights_count} highlight regions"
        )
        return result

    async def _fetch_organization_logo(self) -> bytes | None:
        """Fetch the organization logo image bytes from S3."""
        try:
            stmt = select(Organization).limit(1)
            result = await self.session.execute(stmt)
            org = result.scalar_one_or_none()

            if not org or not org.logo_file_id:
                logger.debug("No organization logo found")
                return None

            file_stmt = select(File).where(File.id == org.logo_file_id)
            file_result = await self.session.execute(file_stmt)
            logo_file = file_result.scalar_one_or_none()

            if not logo_file:
                logger.debug(f"Logo file {org.logo_file_id} not found")
                return None

            s3_key = logo_file.full_path
            file_obj = await self.s3_service.download(key=s3_key)
            logo_data = file_obj.read()
            logger.info(f"Fetched organization logo: {len(logo_data)} bytes")
            return logo_data

        except Exception as e:
            logger.warning(f"Failed to fetch organization logo: {e}")
            return None

    async def _get_spec_sheets_by_ids(self, ids: list[UUID]) -> list[SpecSheet]:
        stmt = select(SpecSheet).where(SpecSheet.id.in_(ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def _download_spec_sheet_pdf(self, spec_sheet: SpecSheet) -> bytes | None:
        try:
            if not spec_sheet.file_url:
                logger.error(f"Spec sheet {spec_sheet.id} has no file_url")
                return None

            url_info = S3Service.extract_url_info(spec_sheet.file_url)
            s3_key = url_info.key

            if not s3_key:
                logger.error(
                    f"No S3 key extracted from spec sheet {spec_sheet.id} "
                    f"file_url: {spec_sheet.file_url[:120]}"
                )
                return None

            # Remove tenant prefix if present, since s3_service.download() adds it
            tenant_prefix = f"{self.s3_service.tenant_name}/"
            if s3_key.startswith(tenant_prefix):
                s3_key = s3_key[len(tenant_prefix) :]

            logger.info(f"Downloading spec sheet {spec_sheet.id} from S3 key: {s3_key}")
            file_obj = await self.s3_service.download(key=s3_key)
            data = file_obj.read()
            logger.info(f"Downloaded spec sheet {spec_sheet.id}: {len(data)} bytes")
            return data

        except Exception as e:
            logger.error(
                f"Failed to download spec sheet PDF {spec_sheet.id}: {e}",
                exc_info=True,
            )
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
