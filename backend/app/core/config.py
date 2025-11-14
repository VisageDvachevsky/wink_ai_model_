from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Movie Rating Backend"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: str = (
        "postgresql+asyncpg://rating_user:rating_pass@localhost:5432/rating_db"
    )

    redis_url: str = "redis://localhost:6379/0"

    ml_service_url: str = "http://localhost:8001"
    ml_service_timeout: int = 300
    ml_service_max_retries: int = 3
    ml_service_retry_delay: float = 2.0

    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    max_upload_size_mb: int = 10
    allowed_file_extensions: list[str] = [".txt", ".pdf", ".doc", ".docx"]

    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
