from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Ecclesia Next"
    environment: str = "development"
    secret_key: str
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 14
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    frontend_url: str = "http://localhost:3000"

    ai_provider: str = "openai"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    google_ai_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash"

    mail_server: str = "smtp.gmail.com"
    mail_port: int = 587
    mail_use_tls: bool = True
    mail_username: str | None = None
    mail_password: str | None = None
    mail_default_sender: str | None = None

    storage_provider: str = "local"
    local_upload_dir: str = "./uploads"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings():
    return Settings()
