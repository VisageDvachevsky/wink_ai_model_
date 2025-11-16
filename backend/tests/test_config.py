import pytest
from pydantic import ValidationError
from app.core.config import Settings


def test_settings_default_values():
    settings = Settings()
    assert settings.app_name == "Movie Rating Backend"
    assert settings.app_version == "1.0.0"
    assert settings.debug is False


def test_settings_database_url_validation():
    with pytest.raises(ValidationError) as exc_info:
        Settings(database_url="mysql://localhost/db")
    assert "DATABASE_URL must be a PostgreSQL" in str(exc_info.value)


def test_settings_redis_url_validation():
    with pytest.raises(ValidationError) as exc_info:
        Settings(redis_url="http://localhost:6379")
    assert "REDIS_URL must start with redis://" in str(exc_info.value)


def test_settings_ml_service_url_validation():
    with pytest.raises(ValidationError) as exc_info:
        Settings(ml_service_url="localhost:8001")
    assert "ML_SERVICE_URL must be a valid HTTP/HTTPS URL" in str(exc_info.value)


def test_get_arq_settings():
    settings = Settings(redis_url="redis://localhost:6379/0")
    arq_settings = settings.get_arq_settings()

    assert arq_settings.host == "localhost"
    assert arq_settings.port == 6379
    assert arq_settings.database == 0


def test_get_arq_settings_custom_port():
    settings = Settings(redis_url="redis://example.com:6380/2")
    arq_settings = settings.get_arq_settings()

    assert arq_settings.host == "example.com"
    assert arq_settings.port == 6380
    assert arq_settings.database == 2


def test_settings_environment_override(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+asyncpg://test:test@testdb:5432/testdb"
    )
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    settings = Settings()
    assert "testdb" in settings.database_url
    assert settings.log_level == "DEBUG"
