from pydantic import field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache
from arq.connections import RedisSettings


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

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith("postgresql"):
            raise ValueError("DATABASE_URL must be a PostgreSQL connection string")
        return v

    @field_validator("redis_url")
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        if not v.startswith("redis://"):
            raise ValueError("REDIS_URL must start with redis://")
        return v

    @field_validator("ml_service_url")
    @classmethod
    def validate_ml_service_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("ML_SERVICE_URL must be a valid HTTP/HTTPS URL")
        return v

    def get_arq_settings(self) -> RedisSettings:
        parts = self.redis_url.replace("redis://", "").split("/")
        host_port = parts[0].split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 6379
        database = int(parts[1]) if len(parts) > 1 else 0

        return RedisSettings(host=host, port=port, database=database)

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
