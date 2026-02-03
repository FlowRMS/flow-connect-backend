from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkOSSettings(BaseSettings):
    workos_api_key: str
    workos_client_id: str
    workos_webhook_secret: str = ""

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
        env_file=(".env", ".env.local", ".env.staging", ".env.production"),
    )
