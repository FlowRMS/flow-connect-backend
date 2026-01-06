from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class VectorSettings(BaseSettings):
    voyage_api_key: str = Field(alias="VOYAGE_API_KEY")
    qdrant_url: str = Field(alias="VECTOR_URL")
    qdrant_api_key: str = Field(alias="VECTOR_API_KEY")

    job_embeddings_collection: str = "job_embeddings"
    duplicate_threshold: float = 0.70
    high_confidence_threshold: float = 0.85

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
        env_file=(".env", ".env.local", ".env.staging", ".env.production"),
        populate_by_name=True,
    )
