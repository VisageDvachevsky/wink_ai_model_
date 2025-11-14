import pytest
from unittest.mock import patch, MagicMock
from app.services.queue import enqueue_rating_job, get_job_status


def test_enqueue_rating_job():
    with patch("app.services.queue.queue") as mock_queue:
        mock_job = MagicMock()
        mock_job.id = "job-123"
        mock_queue.enqueue.return_value = mock_job

        job_id = enqueue_rating_job(42)

        assert job_id == "job-123"
        mock_queue.enqueue.assert_called_once()


def test_get_job_status_queued():
    with patch("app.services.queue.Job.fetch") as mock_fetch:
        mock_job = MagicMock()
        mock_job.get_status.return_value = "queued"
        mock_job.result = None
        mock_fetch.return_value = mock_job

        status = get_job_status("job-123")

        assert status["status"] == "queued"
        assert status["result"] is None


def test_get_job_status_finished():
    with patch("app.services.queue.Job.fetch") as mock_fetch:
        mock_job = MagicMock()
        mock_job.get_status.return_value = "finished"
        mock_job.result = {"predicted_rating": "PG-13"}
        mock_fetch.return_value = mock_job

        status = get_job_status("job-123")

        assert status["status"] == "finished"
        assert status["result"]["predicted_rating"] == "PG-13"


def test_get_job_status_failed():
    with patch("app.services.queue.Job.fetch") as mock_fetch:
        mock_job = MagicMock()
        mock_job.get_status.return_value = "failed"
        mock_job.exc_info = "Error message"
        mock_fetch.return_value = mock_job

        status = get_job_status("job-123")

        assert status["status"] == "failed"
        assert "error" in status


def test_get_job_status_not_found():
    with patch("app.services.queue.Job.fetch") as mock_fetch:
        mock_fetch.side_effect = Exception("Job not found")

        status = get_job_status("invalid-job")

        assert status["status"] == "not_found"
