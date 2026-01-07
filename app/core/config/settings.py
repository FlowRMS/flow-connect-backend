from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    pg_url: PostgresDsn
    ro_pg_host: str
    redis_url: RedisDsn
    environment: str

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        extra="ignore",
        env_file=(".env", ".env.local", ".env.dev", ".env.staging", ".env.prod"),
    )
