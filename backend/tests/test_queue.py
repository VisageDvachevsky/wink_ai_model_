import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from arq.jobs import JobStatus
from app.services.queue import enqueue_rating_job, get_job_status


@pytest.mark.asyncio
async def test_enqueue_rating_job():
    mock_pool = AsyncMock()
    mock_job = MagicMock()
    mock_job.job_id = "test-job-123"
    mock_pool.enqueue_job = AsyncMock(return_value=mock_job)
    mock_pool.close = AsyncMock()

    with patch("app.services.queue.get_arq_pool", return_value=mock_pool):
        job_id = await enqueue_rating_job(script_id=42)

        assert job_id == "test-job-123"
        mock_pool.enqueue_job.assert_called_once_with("process_script_rating", 42)
        mock_pool.close.assert_called_once()


@pytest.mark.asyncio
async def test_get_job_status_not_found():
    mock_pool = AsyncMock()
    mock_pool.job_info = AsyncMock(return_value=None)
    mock_pool.close = AsyncMock()

    with patch("app.services.queue.get_arq_pool", return_value=mock_pool):
        status = await get_job_status("nonexistent-job")

        assert status["job_id"] == "nonexistent-job"
        assert status["status"] == "not_found"
        assert status["result"] is None


@pytest.mark.asyncio
async def test_get_job_status_queued():
    mock_pool = AsyncMock()
    mock_job_info = MagicMock()
    mock_job_info.status = JobStatus.queued
    mock_job_info.result = None
    mock_pool.job_info = AsyncMock(return_value=mock_job_info)
    mock_pool.close = AsyncMock()

    with patch("app.services.queue.get_arq_pool", return_value=mock_pool):
        status = await get_job_status("test-job-123")

        assert status["status"] == "queued"
        assert status["result"] is None


@pytest.mark.asyncio
async def test_get_job_status_complete():
    mock_pool = AsyncMock()
    mock_job_info = MagicMock()
    mock_job_info.status = JobStatus.complete
    mock_job_info.result = {"predicted_rating": "12+"}
    mock_pool.job_info = AsyncMock(return_value=mock_job_info)
    mock_pool.close = AsyncMock()

    with patch("app.services.queue.get_arq_pool", return_value=mock_pool):
        status = await get_job_status("test-job-123")

        assert status["status"] == "completed"
        assert status["result"] == {"predicted_rating": "12+"}
        assert status["error"] is None


@pytest.mark.asyncio
async def test_get_job_status_in_progress():
    mock_pool = AsyncMock()
    mock_job_info = MagicMock()
    mock_job_info.status = JobStatus.in_progress
    mock_job_info.result = None
    mock_pool.job_info = AsyncMock(return_value=mock_job_info)
    mock_pool.close = AsyncMock()

    with patch("app.services.queue.get_arq_pool", return_value=mock_pool):
        status = await get_job_status("test-job-123")

        assert status["status"] == "in_progress"


@pytest.mark.asyncio
async def test_get_job_status_error():
    mock_pool = AsyncMock()
    mock_pool.job_info = AsyncMock(side_effect=Exception("Redis connection error"))
    mock_pool.close = AsyncMock()

    with patch("app.services.queue.get_arq_pool", return_value=mock_pool):
        status = await get_job_status("test-job-123")

        assert status["status"] == "error"
        assert "Redis connection error" in status["error"]
