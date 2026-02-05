from pydantic_settings import BaseSettings, SettingsConfigDict


class VectorSettings(BaseSettings):
    """Settings for vectorization."""

    vector_url: str
    vector_api_key: str
    voyage_api_key: str

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
        env_file=(".env", ".env.local", ".env.staging", ".env.production"),
    )
