"""GraphQL response type for estimate recipients query."""

import strawberry

from app.graphql.contacts.strawberry.contact_response import ContactResponse


@strawberry.type
class EstimateRecipientsResponse:
    """Response for estimate recipients query.

    Returns the total count of matching contacts and a sample of actual
    contact records for preview in the UI.
    """

    count: int
    sample_contacts: list[ContactResponse]
