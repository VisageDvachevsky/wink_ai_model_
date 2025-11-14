import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from app.services.ml_client import MLServiceClient
from app.core.exceptions import MLServiceError, MLServiceTimeoutError


@pytest.fixture
def ml_client():
    return MLServiceClient()


@pytest.mark.asyncio
async def test_rate_script_success(ml_client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "predicted_rating": "12+",
        "agg_scores": {},
        "model_version": "v1.0",
        "total_scenes": 5,
        "top_trigger_scenes": [],
        "reasons": [],
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        result = await ml_client.rate_script("Test script", "script_1")

        assert result["predicted_rating"] == "12+"
        assert result["model_version"] == "v1.0"


@pytest.mark.asyncio
async def test_rate_script_timeout_with_retry(ml_client):
    ml_client.max_retries = 3
    ml_client.retry_delay = 0.01

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
        mock_client_class.return_value = mock_client

        with pytest.raises(MLServiceTimeoutError):
            await ml_client.rate_script("Test script")


@pytest.mark.asyncio
async def test_rate_script_http_error(ml_client):
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_error = httpx.HTTPStatusError(
            "Server error", request=MagicMock(), response=mock_response
        )
        mock_client.post = AsyncMock(side_effect=mock_error)
        mock_client_class.return_value = mock_client

        with pytest.raises(MLServiceError) as exc_info:
            await ml_client.rate_script("Test script")
        assert "500" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_rate_script_connection_error_with_retry(ml_client):
    ml_client.max_retries = 2
    ml_client.retry_delay = 0.01

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = AsyncMock()
        mock_client.post = AsyncMock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        mock_client_class.return_value = mock_client

        with pytest.raises(MLServiceError) as exc_info:
            await ml_client.rate_script("Test script")
        assert "Connection failed" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_health_check_success(ml_client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "status": "healthy",
        "model_version": "v1.0",
        "model_loaded": True,
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        result = await ml_client.health_check()

        assert result["status"] == "healthy"
        assert result["model_loaded"] is True


@pytest.mark.asyncio
async def test_health_check_failure(ml_client):
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("Connection error"))
        mock_client_class.return_value = mock_client

        with pytest.raises(MLServiceError) as exc_info:
            await ml_client.health_check()
        assert "Health check failed" in str(exc_info.value.detail)
