from typing import List
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings for MailTrace AI Backend foundation.
    Reads values from environment variables or a local `.env` file.
    """
    APP_NAME: str = "MailTrace AI Backend"
    API_PREFIX: str = "/api"
    ENVIRONMENT: str = "development"
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @model_validator(mode="after")
    def ensure_frontend_origin_in_allowed(self):
        if self.FRONTEND_ORIGIN and self.FRONTEND_ORIGIN not in self.ALLOWED_ORIGINS:
            self.ALLOWED_ORIGINS.append(self.FRONTEND_ORIGIN)
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
