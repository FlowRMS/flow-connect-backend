from commons.logging.datadog_settings import DatadogSettings
from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    pg_url: PostgresDsn
    ro_pg_host: str
    redis_url: RedisDsn
    environment: str
    datadog: DatadogSettings

    log_level: str = "INFO"

    @property
    def frontend_base_url(self) -> str:
        if self.environment == "production":
            return "https://console.flowrms.com"
        return f"https://{self.environment}.console.flowrms.com"

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        extra="ignore",
        env_file=(".env", ".env.local", ".env.dev", ".env.staging", ".env.prod"),
    )
