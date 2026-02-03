from datetime import datetime

import strawberry


@strawberry.type
class O365ConnectionStatusType:
    """Status of user's O365 connection."""

    is_connected: bool
    microsoft_email: str | None = None
    expires_at: datetime | None = None
    last_used_at: datetime | None = None


@strawberry.input
class O365SendEmailInput:
    """Input for sending an email via O365."""

    to: list[str]
    subject: str
    body: str
    body_type: str = "HTML"
    cc: list[str] | None = None
    bcc: list[str] | None = None


@strawberry.type
class O365SendEmailResultType:
    """Result of sending an email via O365."""

    success: bool
    message_id: str | None = None
    error: str | None = None


@strawberry.type
class O365ConnectionResultType:
    """Result of OAuth connection."""

    success: bool
    microsoft_email: str | None = None
    error: str | None = None


@strawberry.type
class O365CalendarAttendeeType:
    """Attendee for a calendar event."""

    email: str
    name: str | None = None
    response_status: str | None = None


@strawberry.type
class O365CalendarEventType:
    """Calendar event from O365."""

    id: str
    subject: str
    start: datetime
    end: datetime
    is_all_day: bool = False
    location: str | None = None
    body_preview: str | None = None
    organizer_email: str | None = None
    organizer_name: str | None = None
    attendees: list[O365CalendarAttendeeType] | None = None
    web_link: str | None = None
    is_cancelled: bool = False


@strawberry.type
class O365CalendarEventsResultType:
    """Result of fetching calendar events."""

    success: bool
    events: list[O365CalendarEventType] | None = None
    error: str | None = None


@strawberry.type
class O365ContactEmailType:
    address: str
    name: str | None = None


@strawberry.type
class O365ContactType:
    id: str
    display_name: str
    given_name: str | None = None
    surname: str | None = None
    email_addresses: list[O365ContactEmailType] | None = None
    business_phones: list[str] | None = None
    mobile_phone: str | None = None
    home_phones: list[str] | None = None
    job_title: str | None = None
    company_name: str | None = None
    department: str | None = None
    business_address_city: str | None = None
    business_address_state: str | None = None
    business_address_country: str | None = None


@strawberry.type
class O365ContactsResultType:
    success: bool
    contacts: list[O365ContactType] | None = None
    error: str | None = None
