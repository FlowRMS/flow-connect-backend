"""S3 storage settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class S3Settings(BaseSettings):
    """Settings for S3 storage."""

    aws_access_key_id: str
    aws_secret_access_key: str
    aws_endpoint_url: str  # e.g., "https://nyc3.digitaloceanspaces.com"
    aws_bucket_name: str  # e.g., "flowrms-uploads"
    aws_default_region: str = "nyc3"

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
        env_file=(".env", ".env.staging", ".env.production"),
    )
