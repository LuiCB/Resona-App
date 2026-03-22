import os

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    app_name: str = "Resona Backend"
    env: str = "dev"
    api_prefix: str = "/api/v1"
    database_url: str = f"sqlite:///{os.path.join(_BACKEND_DIR, 'resona.db')}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
