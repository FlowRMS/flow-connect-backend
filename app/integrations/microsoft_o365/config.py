from pydantic_settings import BaseSettings, SettingsConfigDict


class O365Settings(BaseSettings):
    """Settings for Microsoft O365 OAuth integration."""

    o365_client_id: str
    o365_client_secret: str
    o365_redirect_uri: str  # e.g., "https://yourapp.com/api/integrations/o365/callback"
    o365_frontend_url: str | None = (
        None  # Optional: frontend URL for local dev (e.g., "http://localhost:3000")
    )

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
        env_file=(".env", ".env.local", ".env.staging", ".env.production"),
    )
