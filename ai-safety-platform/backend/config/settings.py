from __future__ import annotations

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE_PATH = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    project_name: str = "AI Safety & Smart FIR Platform"
    api_version: str = "2.0.0"
    environment: str = "development"

    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "ai_safety_platform"

    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""
    cloudinary_folder: str = "ai-safety-platform/evidence"

    hf_model_name: str = "unitary/toxic-bert"
    tesseract_cmd: str | None = None
    max_upload_mb: int = 10

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    frontend_base_url: str = "http://localhost:3000"

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()

