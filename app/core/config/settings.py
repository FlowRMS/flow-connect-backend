from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    pg_url: PostgresDsn
    environment: str

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        extra="ignore",
        env_file=(".env", ".env.dev", ".env.staging", ".env.prod"),
    )
