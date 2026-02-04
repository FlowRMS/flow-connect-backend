from pydantic_settings import BaseSettings, SettingsConfigDict


class GmailSettings(BaseSettings):
    """Settings for Gmail OAuth integration."""

    gmail_client_id: str
    gmail_client_secret: str
    gmail_redirect_uri: (
        str  # e.g., "https://yourapp.com/api/integrations/gmail/callback"
    )
    gmail_frontend_url: str | None = None  # Optional: frontend URL for local dev

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
        env_file=(".env", ".env.local", ".env.staging", ".env.production"),
    )
