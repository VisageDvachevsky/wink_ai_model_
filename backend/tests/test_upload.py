import pytest
from httpx import AsyncClient
from io import BytesIO


@pytest.mark.asyncio
async def test_upload_valid_file(client: AsyncClient):
    content = b"INT. HOUSE - DAY\n\nJohn enters the room."
    files = {"file": ("script.txt", BytesIO(content), "text/plain")}
    data = {"title": "Test Upload"}

    response = await client.post("/api/v1/scripts/upload", files=files, data=data)
    assert response.status_code == 201

    result = response.json()
    assert result["title"] == "Test Upload"
    assert result["id"] is not None


@pytest.mark.asyncio
async def test_upload_no_extension(client: AsyncClient):
    content = b"INT. HOUSE - DAY"
    files = {"file": ("script", BytesIO(content), "text/plain")}

    response = await client.post("/api/v1/scripts/upload", files=files)
    assert response.status_code == 400
    assert "extension" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_upload_invalid_extension(client: AsyncClient):
    content = b"INT. HOUSE - DAY"
    files = {"file": ("script.pdf", BytesIO(content), "application/pdf")}

    response = await client.post("/api/v1/scripts/upload", files=files)
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_upload_too_large_file(client: AsyncClient):
    content = b"X" * (100 * 1024 * 1024 + 1)
    files = {"file": ("script.txt", BytesIO(content), "text/plain")}

    response = await client.post("/api/v1/scripts/upload", files=files)
    assert response.status_code == 413


@pytest.mark.asyncio
async def test_upload_non_utf8(client: AsyncClient):
    content = b"\xff\xfe\xfd"
    files = {"file": ("script.txt", BytesIO(content), "text/plain")}

    response = await client.post("/api/v1/scripts/upload", files=files)
    assert response.status_code == 400
    assert "utf-8" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_upload_uses_filename_as_title(client: AsyncClient):
    content = b"INT. HOUSE - DAY\n\nJohn enters."
    files = {"file": ("my_movie.txt", BytesIO(content), "text/plain")}

    response = await client.post("/api/v1/scripts/upload", files=files)
    assert response.status_code == 201
    assert response.json()["title"] == "my_movie.txt"
