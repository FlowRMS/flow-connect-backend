from dataclasses import dataclass

import resend
from loguru import logger
from resend.exceptions import ResendError

from app.core.config.resend_settings import ResendSettings


@dataclass
class EmailResult:
    success: bool
    message_id: str | None = None
    error: str | None = None


class ResendNotificationService:
    def __init__(self, settings: ResendSettings) -> None:
        super().__init__()
        self.settings = settings
        if settings.resend_api_key:
            resend.api_key = settings.resend_api_key

    def send_email(
        self,
        to: str,
        subject: str,
        html_body: str,
    ) -> EmailResult:
        if not self.settings.resend_api_key:
            logger.warning("Resend API key not configured, skipping email")
            return EmailResult(success=False, error="API key not configured")

        try:
            params: resend.Emails.SendParams = {
                "from": self.settings.resend_from_email,
                "to": [to],
                "subject": subject,
                "html": html_body,
            }

            email_response = resend.Emails.send(params)
            message_id = email_response.get("id") if email_response else None

            logger.info(f"Email sent successfully via Resend: {message_id}")
            return EmailResult(success=True, message_id=message_id)

        except ResendError as e:
            error_msg = f"Resend API error: {e}"
            logger.error(error_msg)
            return EmailResult(success=False, error=error_msg)
        except Exception as e:
            error_msg = f"Failed to send email via Resend: {e}"
            logger.exception(error_msg)
            return EmailResult(success=False, error=error_msg)
