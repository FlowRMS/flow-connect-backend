from dataclasses import dataclass
from uuid import UUID

from commons.db.v6.crm.submittals import SubmittalRevision
from loguru import logger

from app.graphql.submittals.repositories.submittals_repository import (
    SubmittalsRepository,
)
from app.graphql.submittals.services.submittal_pdf_export_service import (
    SubmittalPdfExportService,
)
from app.graphql.submittals.services.submittals_email_service import (
    SubmittalsEmailService,
)
from app.graphql.submittals.strawberry.submittal_input import GenerateSubmittalPdfInput


@dataclass
class GenerateSubmittalPdfResult:
    success: bool = False
    error: str | None = None
    pdf_url: str | None = None
    pdf_file_name: str | None = None
    pdf_file_size_bytes: int = 0
    revision: SubmittalRevision | None = None
    email_sent: bool = False
    email_recipients_count: int = 0


class SubmittalsRevisionService:
    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        repository: SubmittalsRepository,
        pdf_export_service: SubmittalPdfExportService,
        email_service: SubmittalsEmailService,
    ) -> None:
        self.repository = repository
        self.pdf_export_service = pdf_export_service
        self.email_service = email_service

    async def create_revision(
        self,
        submittal_id: UUID,
        notes: str | None = None,
        pdf_file_id: UUID | None = None,
        pdf_file_url: str | None = None,
        pdf_file_name: str | None = None,
        pdf_file_size_bytes: int | None = None,
    ) -> SubmittalRevision:
        next_revision = await self.repository.get_next_revision_number(submittal_id)

        revision = SubmittalRevision(
            revision_number=next_revision,
            notes=notes,
            pdf_file_id=pdf_file_id,
            pdf_file_url=pdf_file_url,
            pdf_file_name=pdf_file_name,
            pdf_file_size_bytes=pdf_file_size_bytes,
        )

        created = await self.repository.add_revision(submittal_id, revision)
        logger.info(
            f"Created revision {created.revision_number} for submittal {submittal_id}"
        )
        return created

    async def generate_pdf(
        self, input_data: GenerateSubmittalPdfInput
    ) -> GenerateSubmittalPdfResult:
        submittal = await self.repository.get_by_id_with_relations(
            input_data.submittal_id
        )
        if not submittal:
            logger.warning(f"Submittal {input_data.submittal_id} not found for PDF gen")
            return GenerateSubmittalPdfResult(
                success=False,
                error=f"Submittal with id {input_data.submittal_id} not found",
            )

        export_result = await self.pdf_export_service.export_submittal_pdf(
            submittal=submittal,
            input_data=input_data,
        )

        if not export_result.success:
            logger.error(
                f"Failed to export PDF for submittal {input_data.submittal_id}: "
                f"{export_result.error}"
            )
            return GenerateSubmittalPdfResult(
                success=False,
                error=export_result.error,
            )

        revision = None
        if input_data.create_revision or input_data.save_as_attachment:
            revision = await self.create_revision(
                submittal_id=input_data.submittal_id,
                notes=input_data.revision_notes or "PDF generated",
                pdf_file_url=export_result.pdf_url,
                pdf_file_name=export_result.pdf_file_name,
                pdf_file_size_bytes=export_result.pdf_file_size_bytes,
            )
            logger.info(
                f"Created revision {revision.revision_number} for submittal "
                f"{input_data.submittal_id} after PDF generation"
            )

        logger.info(
            f"Generated PDF for submittal {input_data.submittal_id}: "
            f"{export_result.pdf_file_size_bytes} bytes"
        )

        email_sent = False
        email_recipients_count = 0
        if (
            input_data.output_type in ("email", "email_link")
            and input_data.addressed_to_ids
        ):
            try:
                stakeholders = submittal.stakeholders or []
                submittal_number = submittal.submittal_number or "Submittal"
                job_name = submittal.job.job_name if submittal.job else ""

                (
                    email_sent,
                    email_recipients_count,
                ) = await self.email_service.send_pdf_email(
                    submittal_id=input_data.submittal_id,
                    stakeholders=stakeholders,
                    addressed_to_ids=input_data.addressed_to_ids,
                    output_type=input_data.output_type,
                    pdf_url=export_result.pdf_url,
                    pdf_file_name=export_result.pdf_file_name,
                    submittal_number=submittal_number,
                    job_name=job_name,
                    revision_id=revision.id if revision else None,
                )
            except Exception as e:
                logger.error(
                    f"Error sending email for submittal {input_data.submittal_id}: {e}"
                )

        return GenerateSubmittalPdfResult(
            success=True,
            pdf_url=export_result.pdf_url,
            pdf_file_name=export_result.pdf_file_name,
            pdf_file_size_bytes=export_result.pdf_file_size_bytes,
            revision=revision,
            email_sent=email_sent,
            email_recipients_count=email_recipients_count,
        )
