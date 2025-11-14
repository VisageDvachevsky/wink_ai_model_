import pytest
from httpx import AsyncClient
from io import BytesIO
import asyncio


@pytest.mark.asyncio
async def test_upload_rate_limit(client: AsyncClient):
    content = b"INT. HOUSE - DAY"

    responses = []
    for i in range(12):
        files = {"file": (f"script{i}.txt", BytesIO(content), "text/plain")}
        response = await client.post("/api/v1/scripts/upload", files=files)
        responses.append(response.status_code)

    assert 429 in responses


@pytest.mark.asyncio
async def test_rate_script_rate_limit(client: AsyncClient, sample_script):
    responses = []
    for i in range(25):
        response = await client.post(
            f"/api/v1/scripts/{sample_script.id}/rate?background=true"
        )
        responses.append(response.status_code)

    assert 429 in responses
