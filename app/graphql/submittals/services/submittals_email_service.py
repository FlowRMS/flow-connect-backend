from uuid import UUID

import httpx
from commons.db.v6.crm.submittals import SubmittalEmail
from loguru import logger

from app.graphql.campaigns.services.email_provider_service import (
    EmailAttachment,
    EmailProviderService,
)
from app.graphql.submittals.repositories.submittals_repository import (
    SubmittalsRepository,
)
from app.graphql.submittals.services.types import SendSubmittalEmailResult
from app.graphql.submittals.strawberry.submittal_input import SendSubmittalEmailInput


class SubmittalsEmailService:
    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        repository: SubmittalsRepository,
        email_provider: EmailProviderService,
    ) -> None:
        self.repository = repository
        self.email_provider = email_provider

    async def send_email(
        self, input_data: SendSubmittalEmailInput
    ) -> SendSubmittalEmailResult:
        has_provider = await self.email_provider.has_connected_provider()
        if not has_provider:
            logger.warning("Cannot send submittal email: no email provider connected")
            return SendSubmittalEmailResult(
                success=False,
                error="No email provider connected. Please connect O365 or Gmail in settings.",
            )

        attachments: list[EmailAttachment] = []
        if input_data.attachment_url:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(input_data.attachment_url, timeout=60.0)
                    _ = response.raise_for_status()
                    attachment_content = response.content
                    attachment_name = input_data.attachment_name or "submittal.pdf"
                    attachments.append(
                        EmailAttachment(
                            filename=attachment_name,
                            content=attachment_content,
                            content_type="application/pdf",
                        )
                    )
                    logger.info(
                        f"Downloaded attachment {attachment_name} "
                        f"({len(attachment_content)} bytes)"
                    )
            except Exception as e:
                logger.error(f"Failed to download attachment: {e}")
                return SendSubmittalEmailResult(
                    success=False,
                    error=f"Failed to download PDF attachment: {e!s}",
                )

        send_result = await self.email_provider.send_email(
            to=input_data.recipient_emails,
            subject=input_data.subject,
            body=input_data.body or "",
            body_type="HTML",
            attachments=attachments if attachments else None,
        )

        if not send_result.success:
            logger.error(f"Failed to send submittal email: {send_result.error}")
            return SendSubmittalEmailResult(
                success=False,
                error=send_result.error,
                send_result=send_result,
            )

        email = SubmittalEmail(
            revision_id=input_data.revision_id,
            subject=input_data.subject,
            body=input_data.body,
            recipient_emails=input_data.recipient_emails,
            recipients=[
                {"email": e, "type": "to"} for e in input_data.recipient_emails
            ],
        )
        email.created_by_id = self.email_provider.auth_info.flow_user_id

        created = await self.repository.add_email(input_data.submittal_id, email)
        logger.info(
            f"Sent and recorded email for submittal {input_data.submittal_id} "
            f"to {len(input_data.recipient_emails)} recipients via {send_result.provider}"
        )

        return SendSubmittalEmailResult(
            email_record=created,
            send_result=send_result,
            success=True,
        )

    async def send_pdf_email(
        self,
        submittal_id: UUID,
        stakeholders: list,
        addressed_to_ids: list[UUID],
        output_type: str,
        pdf_url: str | None,
        pdf_file_name: str | None,
        submittal_number: str,
        job_name: str,
        revision_id: UUID | None,
    ) -> tuple[bool, int]:
        addressed_to_ids_str = {str(sid) for sid in addressed_to_ids}
        recipient_emails = [
            s.contact_email
            for s in stakeholders
            if str(s.id) in addressed_to_ids_str and s.contact_email
        ]

        if not recipient_emails:
            logger.warning(
                f"No valid recipient emails found for submittal "
                f"{submittal_id} addressed-to stakeholders"
            )
            return False, 0

        subject = f"Submittal {submittal_number} - {job_name}".strip(" -")

        if output_type == "email":
            attachments: list[EmailAttachment] = []
            if pdf_url:
                async with httpx.AsyncClient() as client:
                    response = await client.get(pdf_url, timeout=60.0)
                    _ = response.raise_for_status()
                    attachments.append(
                        EmailAttachment(
                            filename=pdf_file_name or "submittal.pdf",
                            content=response.content,
                            content_type="application/pdf",
                        )
                    )

            body = (
                f"<p>Please find attached the submittal document "
                f"<strong>{submittal_number}</strong>.</p>"
            )
            send_result = await self.email_provider.send_email(
                to=recipient_emails,
                subject=subject,
                body=body,
                body_type="HTML",
                attachments=attachments if attachments else None,
            )
        else:
            body = (
                f"<p>Please review the submittal document "
                f"<strong>{submittal_number}</strong>.</p>"
                f'<p><a href="{pdf_url}">Download PDF</a></p>'
            )
            send_result = await self.email_provider.send_email(
                to=recipient_emails,
                subject=subject,
                body=body,
                body_type="HTML",
            )

        if send_result.success:
            if revision_id:
                email_record = SubmittalEmail(
                    revision_id=revision_id,
                    subject=subject,
                    body=body,
                    recipient_emails=recipient_emails,
                    recipients=[{"email": e, "type": "to"} for e in recipient_emails],
                )
                email_record.created_by_id = self.email_provider.auth_info.flow_user_id
                _ = await self.repository.add_email(submittal_id, email_record)

            logger.info(
                f"Sent submittal {submittal_id} via {output_type} to "
                f"{len(recipient_emails)} recipients"
            )
            return True, len(recipient_emails)

        logger.error(
            f"Failed to send email for submittal {submittal_id}: {send_result.error}"
        )
        return False, 0
