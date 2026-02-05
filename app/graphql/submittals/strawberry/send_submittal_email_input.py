from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import SubmittalEmail

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class SendSubmittalEmailInput(BaseInputGQL[SubmittalEmail]):
    submittal_id: UUID
    revision_id: UUID | None = None
    subject: str
    body: str | None = None
    recipient_emails: list[str]
    attachment_url: str | None = None
    attachment_name: str | None = None
