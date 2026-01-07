from pydantic_settings import BaseSettings, SettingsConfigDict


class ResendSettings(BaseSettings):
    resend_api_key: str = ""
    resend_from_email: str = "FlowAI <noreply@flowrms.com>"
    frontend_base_url: str = "https://app.flowrms.com"

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
        env_file=(".env", ".env.local", ".env.staging", ".env.production"),
    )
