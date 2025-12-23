from pydantic_settings import BaseSettings, SettingsConfigDict


class AdminSettings(BaseSettings):
    admin_org_id: str
    support_user_email: str

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
        env_file=(".env", ".env.local", ".env.staging", ".env.production"),
    )
