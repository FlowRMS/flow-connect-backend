from dataclasses import dataclass

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
class O365ContactEmail:
    address: str
    name: str | None = None


@dataclass
class O365ContactPhone:
    number: str
    type: str | None = None


@dataclass
class O365Contact:
    id: str
    display_name: str
    given_name: str | None = None
    surname: str | None = None
    email_addresses: list[O365ContactEmail] | None = None
    business_phones: list[str] | None = None
    mobile_phone: str | None = None
    home_phones: list[str] | None = None
    job_title: str | None = None
    company_name: str | None = None
    department: str | None = None
    business_address_city: str | None = None
    business_address_state: str | None = None
    business_address_country: str | None = None


@dataclass
class O365ContactsResult:
    success: bool
    contacts: list[O365Contact] | None = None
    error: str | None = None
    next_link: str | None = None


class O365ContactsService:
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
        return await self.auth_service.get_valid_token(self.auth_info.flow_user_id)

    def _parse_contact(self, contact_data: dict) -> O365Contact:
        email_addresses = None
        if contact_data.get("emailAddresses"):
            email_addresses = [
                O365ContactEmail(
                    address=email.get("address", ""),
                    name=email.get("name"),
                )
                for email in contact_data["emailAddresses"]
                if email.get("address")
            ]

        business_address = contact_data.get("businessAddress", {}) or {}

        return O365Contact(
            id=contact_data.get("id", ""),
            display_name=contact_data.get("displayName", ""),
            given_name=contact_data.get("givenName"),
            surname=contact_data.get("surname"),
            email_addresses=email_addresses,
            business_phones=contact_data.get("businessPhones") or None,
            mobile_phone=contact_data.get("mobilePhone"),
            home_phones=contact_data.get("homePhones") or None,
            job_title=contact_data.get("jobTitle"),
            company_name=contact_data.get("companyName"),
            department=contact_data.get("department"),
            business_address_city=business_address.get("city"),
            business_address_state=business_address.get("state"),
            business_address_country=business_address.get("countryOrRegion"),
        )

    async def get_contacts(
        self,
        top: int = 50,
        skip: int = 0,
        search: str | None = None,
    ) -> O365ContactsResult:
        """
        Fetch contacts from Microsoft 365.

        Args:
            top: Maximum number of contacts to return (default 50)
            skip: Number of contacts to skip for pagination
            search: Optional search query to filter contacts by name or email

        Returns:
            O365ContactsResult with contacts or error
        """
        try:
            access_token = await self._get_valid_token()
        except (NotFoundError, O365AuthError) as e:
            return O365ContactsResult(success=False, error=str(e))

        params: dict[str, str] = {
            "$top": str(top),
            "$skip": str(skip),
            "$orderby": "displayName",
            "$select": (
                "id,displayName,givenName,surname,emailAddresses,"
                "businessPhones,mobilePhone,homePhones,jobTitle,"
                "companyName,department,businessAddress"
            ),
        }

        if search:
            params["$filter"] = (
                f"startswith(displayName,'{search}') or "
                f"startswith(givenName,'{search}') or "
                f"startswith(surname,'{search}')"
            )

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MICROSOFT_GRAPH_API}/me/contacts",
                headers={"Authorization": f"Bearer {access_token}"},
                params=params,
                timeout=30.0,
            )

            if response.status_code == 200:
                data = response.json()
                contacts = [self._parse_contact(c) for c in data.get("value", [])]
                return O365ContactsResult(
                    success=True,
                    contacts=contacts,
                    next_link=data.get("@odata.nextLink"),
                )

            error_data = response.json()
            error_message = error_data.get("error", {}).get(
                "message", "Failed to fetch contacts"
            )
            return O365ContactsResult(success=False, error=error_message)

    async def get_contact_by_id(self, contact_id: str) -> O365Contact | None:
        try:
            access_token = await self._get_valid_token()
        except (NotFoundError, O365AuthError):
            return None

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MICROSOFT_GRAPH_API}/me/contacts/{contact_id}",
                headers={"Authorization": f"Bearer {access_token}"},
                params={
                    "$select": (
                        "id,displayName,givenName,surname,emailAddresses,"
                        "businessPhones,mobilePhone,homePhones,jobTitle,"
                        "companyName,department,businessAddress"
                    )
                },
                timeout=30.0,
            )

            if response.status_code == 200:
                return self._parse_contact(response.json())

            return None
