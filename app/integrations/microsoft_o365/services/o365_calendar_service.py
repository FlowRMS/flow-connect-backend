from dataclasses import dataclass
from datetime import datetime

import httpx
from commons.auth import AuthInfo

from app.errors.common_errors import NotFoundError
from app.integrations.microsoft_o365.constants import MICROSOFT_GRAPH_API
from app.integrations.microsoft_o365.repositories.o365_token_repository import (
    O365TokenRepository,
)
from app.integrations.microsoft_o365.services.o365_auth_service import (
    O365AuthError,
    O365AuthService,
)


@dataclass
class CalendarEventAttendee:
    """Attendee for a calendar event."""

    email: str
    name: str | None = None
    response_status: str | None = None


@dataclass
class CalendarEvent:
    """Represents a calendar event from O365."""

    id: str
    subject: str
    start: datetime
    end: datetime
    is_all_day: bool = False
    location: str | None = None
    body_preview: str | None = None
    organizer_email: str | None = None
    organizer_name: str | None = None
    attendees: list[CalendarEventAttendee] | None = None
    web_link: str | None = None
    is_cancelled: bool = False


@dataclass
class CalendarEventsResult:
    """Result of fetching calendar events."""

    success: bool
    events: list[CalendarEvent] | None = None
    error: str | None = None


class O365CalendarService:
    """Service for Microsoft O365 calendar operations."""

    def __init__(
        self,
        repository: O365TokenRepository,
        auth_service: O365AuthService,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_service = auth_service
        self.auth_info = auth_info

    async def _get_valid_token(self) -> str:
        """Get valid access token for current user."""
        return await self.auth_service.get_valid_token(self.auth_info.flow_user_id)

    def _parse_event(self, event_data: dict) -> CalendarEvent:
        """Parse Microsoft Graph API event response into CalendarEvent."""
        attendees = None
        if event_data.get("attendees"):
            attendees = [
                CalendarEventAttendee(
                    email=att.get("emailAddress", {}).get("address", ""),
                    name=att.get("emailAddress", {}).get("name"),
                    response_status=att.get("status", {}).get("response"),
                )
                for att in event_data["attendees"]
            ]

        organizer = event_data.get("organizer", {}).get("emailAddress", {})

        start_data = event_data.get("start", {})
        end_data = event_data.get("end", {})

        start_str = start_data.get("dateTime", "")
        end_str = end_data.get("dateTime", "")

        if start_str.endswith("Z"):
            start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        else:
            start = datetime.fromisoformat(start_str)

        if end_str.endswith("Z"):
            end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        else:
            end = datetime.fromisoformat(end_str)

        return CalendarEvent(
            id=event_data.get("id", ""),
            subject=event_data.get("subject", ""),
            start=start,
            end=end,
            is_all_day=event_data.get("isAllDay", False),
            location=event_data.get("location", {}).get("displayName"),
            body_preview=event_data.get("bodyPreview"),
            organizer_email=organizer.get("address"),
            organizer_name=organizer.get("name"),
            attendees=attendees,
            web_link=event_data.get("webLink"),
            is_cancelled=event_data.get("isCancelled", False),
        )

    async def get_events(
        self,
        top: int = 50,
        skip: int = 0,
        order_by: str = "start/dateTime",
    ) -> CalendarEventsResult:
        """
        Get calendar events for the current user.

        Args:
            top: Maximum number of events to return (default 50)
            skip: Number of events to skip for pagination
            order_by: Field to order by (default: start/dateTime)

        Returns:
            CalendarEventsResult with events or error
        """
        try:
            access_token = await self._get_valid_token()
        except (NotFoundError, O365AuthError) as e:
            return CalendarEventsResult(success=False, error=str(e))

        params = {
            "$top": str(top),
            "$skip": str(skip),
            "$orderby": order_by,
            "$select": "id,subject,start,end,isAllDay,location,bodyPreview,organizer,attendees,webLink,isCancelled",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MICROSOFT_GRAPH_API}/me/events",
                headers={"Authorization": f"Bearer {access_token}"},
                params=params,
            )

            if response.status_code == 200:
                data = response.json()
                events = [self._parse_event(e) for e in data.get("value", [])]
                return CalendarEventsResult(success=True, events=events)

            error_data = response.json()
            error_message = error_data.get("error", {}).get(
                "message", "Failed to fetch calendar events"
            )
            return CalendarEventsResult(success=False, error=error_message)

    async def get_events_in_range(
        self,
        start_date: datetime,
        end_date: datetime,
        top: int = 100,
    ) -> CalendarEventsResult:
        """
        Get calendar events within a specific date range using calendarView.

        Args:
            start_date: Start of the date range
            end_date: End of the date range
            top: Maximum number of events to return (default 100)

        Returns:
            CalendarEventsResult with events or error
        """
        try:
            access_token = await self._get_valid_token()
        except (NotFoundError, O365AuthError) as e:
            return CalendarEventsResult(success=False, error=str(e))

        start_iso = start_date.isoformat()
        end_iso = end_date.isoformat()

        params = {
            "startDateTime": start_iso,
            "endDateTime": end_iso,
            "$top": str(top),
            "$orderby": "start/dateTime",
            "$select": "id,subject,start,end,isAllDay,location,bodyPreview,organizer,attendees,webLink,isCancelled",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MICROSOFT_GRAPH_API}/me/calendarView",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Prefer": 'outlook.timezone="UTC"',
                },
                params=params,
            )

            if response.status_code == 200:
                data = response.json()
                events = [self._parse_event(e) for e in data.get("value", [])]
                return CalendarEventsResult(success=True, events=events)

            error_data = response.json()
            error_message = error_data.get("error", {}).get(
                "message", "Failed to fetch calendar events"
            )
            return CalendarEventsResult(success=False, error=error_message)

    async def get_event_by_id(self, event_id: str) -> CalendarEvent | None:
        """
        Get a specific calendar event by ID.

        Args:
            event_id: The event ID

        Returns:
            CalendarEvent if found, None otherwise
        """
        try:
            access_token = await self._get_valid_token()
        except (NotFoundError, O365AuthError):
            return None

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MICROSOFT_GRAPH_API}/me/events/{event_id}",
                headers={"Authorization": f"Bearer {access_token}"},
                params={
                    "$select": "id,subject,start,end,isAllDay,location,bodyPreview,organizer,attendees,webLink,isCancelled"
                },
            )

            if response.status_code == 200:
                return self._parse_event(response.json())

            return None
