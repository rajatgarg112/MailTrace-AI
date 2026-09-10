import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "MailTrace AI"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./mailtrace.db")

    model_config = ConfigDict(case_sensitive=True)


settings = Settings()

