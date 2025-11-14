import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from app.core.exceptions import ScriptNotFoundError


@pytest.mark.asyncio
async def test_script_not_found_error(client: AsyncClient):
    response = await client.get("/api/v1/scripts/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_rate_nonexistent_script(client: AsyncClient):
    response = await client.post("/api/v1/scripts/99999/rate?background=false")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_invalid_file_error_validation(client: AsyncClient):
    payload = {"title": "", "content": "x"}
    response = await client.post("/api/v1/scripts/", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ml_service_failure_rollback(client: AsyncClient, sample_script):
    with patch("app.services.ml_client.ml_client.rate_script") as mock_rate:
        mock_rate.side_effect = Exception("ML service down")

        response = await client.post(
            f"/api/v1/scripts/{sample_script.id}/rate?background=false"
        )
        assert response.status_code == 500

        check_response = await client.get(f"/api/v1/scripts/{sample_script.id}")
        assert check_response.status_code == 200
        script = check_response.json()
        assert script["predicted_rating"] is None
