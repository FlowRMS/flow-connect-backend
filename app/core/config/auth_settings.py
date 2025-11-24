from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    auth_url: str
    client_id: str
    client_secret: str

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
        env_file=(".env", ".env.staging", ".env.production"),
    )
