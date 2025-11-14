import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_pagination_default(client: AsyncClient):
    response = await client.get("/api/v1/scripts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_pagination_negative_skip(client: AsyncClient):
    response = await client.get("/api/v1/scripts/?skip=-1")
    assert response.status_code == 400
    assert "non-negative" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_pagination_zero_limit(client: AsyncClient):
    response = await client.get("/api/v1/scripts/?limit=0")
    assert response.status_code == 400
    assert "between 1 and 1000" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_pagination_too_large_limit(client: AsyncClient):
    response = await client.get("/api/v1/scripts/?limit=1001")
    assert response.status_code == 400
    assert "between 1 and 1000" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_pagination_valid_range(client: AsyncClient):
    response = await client.get("/api/v1/scripts/?skip=0&limit=10")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_pagination_max_limit(client: AsyncClient):
    response = await client.get("/api/v1/scripts/?limit=1000")
    assert response.status_code == 200
