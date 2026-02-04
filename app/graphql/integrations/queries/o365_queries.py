from datetime import datetime

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.integrations.o365_types import (
    O365CalendarAttendeeType,
    O365CalendarEventsResultType,
    O365CalendarEventType,
    O365ConnectionStatusType,
    O365ContactEmailType,
    O365ContactsResultType,
    O365ContactType,
)
from app.integrations.microsoft_o365.services.o365_auth_service import O365AuthService
from app.integrations.microsoft_o365.services.o365_calendar_service import (
    O365CalendarService,
)
from app.integrations.microsoft_o365.services.o365_contacts_service import (
    O365ContactsService,
)


@strawberry.type
class O365Queries:
    """GraphQL queries for O365 integration."""

    @strawberry.field
    @inject
    async def o365_auth_url(
        self,
        service: Injected[O365AuthService],
        state: str | None = None,
    ) -> str:
        """
        Get OAuth authorization URL for Microsoft O365.

        Args:
            state: Optional state parameter for CSRF protection

        Returns:
            Authorization URL to redirect user to
        """
        return service.get_authorization_url(state)

    @strawberry.field
    @inject
    async def o365_connection_status(
        self,
        service: Injected[O365AuthService],
    ) -> O365ConnectionStatusType:
        """Check current user's O365 connection status."""
        status = await service.get_connection_status()
        return O365ConnectionStatusType(
            is_connected=status.is_connected,
            microsoft_email=status.microsoft_email,
            expires_at=status.expires_at,
            last_used_at=status.last_used_at,
        )

    @strawberry.field
    @inject
    async def o365_calendar_events(
        self,
        service: Injected[O365CalendarService],
        top: int = 50,
        skip: int = 0,
    ) -> O365CalendarEventsResultType:
        """
        Get calendar events for the current user.

        Args:
            top: Maximum number of events to return (default 50)
            skip: Number of events to skip for pagination

        Returns:
            O365CalendarEventsResultType with events or error
        """
        result = await service.get_events(top=top, skip=skip)

        if not result.success:
            return O365CalendarEventsResultType(
                success=False,
                error=result.error,
            )

        events = [
            O365CalendarEventType(
                id=e.id,
                subject=e.subject,
                start=e.start,
                end=e.end,
                is_all_day=e.is_all_day,
                location=e.location,
                body_preview=e.body_preview,
                organizer_email=e.organizer_email,
                organizer_name=e.organizer_name,
                attendees=[
                    O365CalendarAttendeeType(
                        email=a.email,
                        name=a.name,
                        response_status=a.response_status,
                    )
                    for a in e.attendees
                ]
                if e.attendees
                else None,
                web_link=e.web_link,
                is_cancelled=e.is_cancelled,
            )
            for e in (result.events or [])
        ]

        return O365CalendarEventsResultType(success=True, events=events)

    @strawberry.field
    @inject
    async def o365_calendar_events_in_range(
        self,
        service: Injected[O365CalendarService],
        start_date: datetime,
        end_date: datetime,
        top: int = 100,
    ) -> O365CalendarEventsResultType:
        """
        Get calendar events within a specific date range.

        Args:
            start_date: Start of the date range
            end_date: End of the date range
            top: Maximum number of events to return (default 100)

        Returns:
            O365CalendarEventsResultType with events or error
        """
        result = await service.get_events_in_range(
            start_date=start_date,
            end_date=end_date,
            top=top,
        )

        if not result.success:
            return O365CalendarEventsResultType(
                success=False,
                error=result.error,
            )

        events = [
            O365CalendarEventType(
                id=e.id,
                subject=e.subject,
                start=e.start,
                end=e.end,
                is_all_day=e.is_all_day,
                location=e.location,
                body_preview=e.body_preview,
                organizer_email=e.organizer_email,
                organizer_name=e.organizer_name,
                attendees=[
                    O365CalendarAttendeeType(
                        email=a.email,
                        name=a.name,
                        response_status=a.response_status,
                    )
                    for a in e.attendees
                ]
                if e.attendees
                else None,
                web_link=e.web_link,
                is_cancelled=e.is_cancelled,
            )
            for e in (result.events or [])
        ]

        return O365CalendarEventsResultType(success=True, events=events)

    @strawberry.field
    @inject
    async def o365_contacts(
        self,
        service: Injected[O365ContactsService],
        top: int = 50,
        skip: int = 0,
        search: str | None = None,
    ) -> O365ContactsResultType:
        """
        Get contacts from Microsoft 365.

        Args:
            top: Maximum number of contacts to return (default 50)
            skip: Number of contacts to skip for pagination
            search: Optional search query to filter contacts by name

        Returns:
            O365ContactsResultType with contacts or error
        """
        result = await service.get_contacts(top=top, skip=skip, search=search)

        if not result.success:
            return O365ContactsResultType(success=False, error=result.error)

        contacts = [
            O365ContactType(
                id=c.id,
                display_name=c.display_name,
                given_name=c.given_name,
                surname=c.surname,
                email_addresses=[
                    O365ContactEmailType(address=e.address, name=e.name)
                    for e in c.email_addresses
                ]
                if c.email_addresses
                else None,
                business_phones=c.business_phones,
                mobile_phone=c.mobile_phone,
                home_phones=c.home_phones,
                job_title=c.job_title,
                company_name=c.company_name,
                department=c.department,
                business_address_city=c.business_address_city,
                business_address_state=c.business_address_state,
                business_address_country=c.business_address_country,
            )
            for c in (result.contacts or [])
        ]

        return O365ContactsResultType(success=True, contacts=contacts)
