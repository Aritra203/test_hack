from pathlib import Path
from typing import List

from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE_PATH = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    project_name: str = "AI Safety & Smart FIR Platform"
    api_version: str = "1.0.0"

    allowed_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "ai_safety_platform"

    cloud_name: str = Field(
        default="",
        validation_alias=AliasChoices("CLOUD_NAME", "CLOUDINARY_CLOUD_NAME"),
    )
    api_key: str = Field(
        default="",
        validation_alias=AliasChoices("API_KEY", "CLOUDINARY_API_KEY"),
    )
    api_secret: str = Field(
        default="",
        validation_alias=AliasChoices("API_SECRET", "CLOUDINARY_API_SECRET"),
    )
    cloudinary_folder: str = "ai-safety-platform/evidence"

    hf_model_name: str = "unitary/toxic-bert"
    tesseract_cmd: str | None = None

    max_upload_mb: int = 10

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def validate_cloudinary_credentials(self) -> "Settings":
        if not all(
            [
                self.cloud_name,
                self.api_key,
                self.api_secret,
            ]
        ):
            raise ValueError(
                "Cloudinary credentials are missing. Set CLOUD_NAME, API_KEY, and API_SECRET."
            )
        return self

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
