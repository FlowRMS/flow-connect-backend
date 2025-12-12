"""Base classes for email sending strategies."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class WorkerSendEmailResult:
    """Result of sending an email in worker context."""

    success: bool
    error: str | None = None


# Buffer time before token expiration to trigger refresh (5 minutes)
TOKEN_REFRESH_BUFFER_SECONDS = 300


class EmailStrategy(ABC):
    """Abstract base class for email sending strategies."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the strategy name for logging."""
        ...

    @abstractmethod
    async def get_token(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> object | None:
        """
        Get the user's token for this email provider.

        Args:
            session: Database session
            user_id: User ID to look up token for

        Returns:
            Token object if available and active, None otherwise
        """
        ...

    @abstractmethod
    async def refresh_token_if_needed(
        self,
        session: AsyncSession,
        token: object,
    ) -> str | None:
        """
        Refresh token if expired or about to expire.

        Args:
            session: Database session for updating token
            token: Token to potentially refresh

        Returns:
            Valid access token or None if refresh failed
        """
        ...

    @abstractmethod
    async def send(
        self,
        access_token: str,
        to: str,
        subject: str,
        body: str,
        sender: str | None = None,
    ) -> WorkerSendEmailResult:
        """
        Send an email using this provider.

        Args:
            access_token: Valid access token
            to: Recipient email address
            subject: Email subject
            body: HTML email body
            sender: Sender email (required for some providers)

        Returns:
            WorkerSendEmailResult with success status
        """
        ...

    async def is_available(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> bool:
        """
        Check if this strategy is available for the user.

        Args:
            session: Database session
            user_id: User ID to check availability for

        Returns:
            True if strategy is available, False otherwise
        """
        token = await self.get_token(session, user_id)
        return token is not None
