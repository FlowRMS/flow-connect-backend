from pydantic_settings import BaseSettings, SettingsConfigDict


class FlowConnectApiSettings(BaseSettings):
    flow_connect_api_url: str | None = None

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
        env_file=(".env", ".env.local", ".env.staging", ".env.production"),
    )
