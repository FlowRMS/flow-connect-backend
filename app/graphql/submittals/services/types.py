from dataclasses import dataclass

from commons.db.v6.crm.submittals import SubmittalEmail

from app.graphql.campaigns.services.email_provider_service import SendEmailResult


@dataclass
class SendSubmittalEmailResult:
    email_record: SubmittalEmail | None = None
    send_result: SendEmailResult | None = None
    success: bool = False
    error: str | None = None
