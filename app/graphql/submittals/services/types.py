"""Type definitions for Submittals services."""

from dataclasses import dataclass
from typing import Optional

from commons.db.v6.crm.submittals import SubmittalEmail

from app.graphql.campaigns.services.email_provider_service import SendEmailResult


@dataclass
class SendSubmittalEmailResult:
    """Result of sending a submittal email."""

    email_record: Optional[SubmittalEmail] = None
    send_result: Optional[SendEmailResult] = None
    success: bool = False
    error: Optional[str] = None
