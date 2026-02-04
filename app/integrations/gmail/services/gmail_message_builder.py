import base64
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.graphql.campaigns.services.email_provider_service import EmailAttachment


def create_message(
    sender: str,
    to: list[str],
    subject: str,
    body: str,
    body_type: str = "HTML",
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    attachments: list["EmailAttachment"] | None = None,
) -> str:
    """
    Create a base64url-encoded RFC 2822 email message suitable for the Gmail API.

    Builds a MIME multipart message with optional attachments, then encodes it
    as a base64url string that can be passed directly to the Gmail send endpoint.
    """
    # Use mixed multipart if we have attachments, otherwise alternative
    if attachments:
        message = MIMEMultipart("mixed")
        # Create a sub-part for the body
        body_part = MIMEMultipart("alternative")
        subtype = "html" if body_type.upper() == "HTML" else "plain"
        body_part.attach(MIMEText(body, subtype))
        message.attach(body_part)
    else:
        message = MIMEMultipart("alternative")
        subtype = "html" if body_type.upper() == "HTML" else "plain"
        message.attach(MIMEText(body, subtype))

    message["From"] = sender
    message["To"] = ", ".join(to)
    message["Subject"] = subject

    if cc:
        message["Cc"] = ", ".join(cc)
    if bcc:
        message["Bcc"] = ", ".join(bcc)

    # Add attachments
    if attachments:
        for att in attachments:
            maintype, subtype = att.content_type.split("/", 1)
            part = MIMEBase(maintype, subtype)
            part.set_payload(att.content)
            encode_base64(part)
            part.add_header(
                "Content-Disposition",
                "attachment",
                filename=att.filename,
            )
            message.attach(part)

    # Encode to base64
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    return raw
