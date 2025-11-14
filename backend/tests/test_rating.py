import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_rate_script_background(client: AsyncClient, sample_script):
    with patch("app.services.queue.enqueue_rating_job") as mock_enqueue:
        mock_enqueue.return_value = "job-123"

        response = await client.post(
            f"/api/v1/scripts/{sample_script.id}/rate?background=true"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "job-123"
        assert data["status"] == "queued"
        mock_enqueue.assert_called_once_with(sample_script.id)


@pytest.mark.asyncio
async def test_rate_script_sync(client: AsyncClient, sample_script):
    mock_result = {
        "predicted_rating": "PG-13",
        "agg_scores": {"violence": 0.3, "gore": 0.1},
        "model_version": "v1.0",
        "total_scenes": 5,
        "top_trigger_scenes": [
            {
                "scene_id": 1,
                "heading": "INT. HOUSE - DAY",
                "violence": 0.5,
                "gore": 0.2,
                "sex_act": 0.0,
                "nudity": 0.0,
                "profanity": 0.1,
                "drugs": 0.0,
                "child_risk": 0.0,
                "weight": 0.3,
            }
        ],
        "reasons": ["Moderate violence"],
    }

    with patch("app.services.ml_client.ml_client.rate_script") as mock_rate:
        mock_rate.return_value = mock_result

        response = await client.post(
            f"/api/v1/scripts/{sample_script.id}/rate?background=false"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "sync"
        assert data["status"] == "completed"

        script_response = await client.get(f"/api/v1/scripts/{sample_script.id}")
        script = script_response.json()
        assert script["predicted_rating"] == "PG-13"
        assert script["total_scenes"] == 5
        assert len(script["scenes"]) == 1


@pytest.mark.asyncio
async def test_rate_script_with_multiple_scenes(client: AsyncClient, sample_script):
    mock_result = {
        "predicted_rating": "R",
        "agg_scores": {"violence": 0.7, "gore": 0.5},
        "model_version": "v1.0",
        "total_scenes": 10,
        "top_trigger_scenes": [
            {
                "scene_id": i,
                "heading": f"SCENE {i}",
                "violence": 0.8,
                "gore": 0.6,
                "sex_act": 0.2,
                "nudity": 0.1,
                "profanity": 0.5,
                "drugs": 0.3,
                "child_risk": 0.4,
                "weight": 0.7,
            }
            for i in range(5)
        ],
        "reasons": ["High violence", "Gore content"],
    }

    with patch("app.services.ml_client.ml_client.rate_script") as mock_rate:
        mock_rate.return_value = mock_result

        response = await client.post(
            f"/api/v1/scripts/{sample_script.id}/rate?background=false"
        )
        assert response.status_code == 200

        script_response = await client.get(f"/api/v1/scripts/{sample_script.id}")
        script = script_response.json()
        assert len(script["scenes"]) == 5


@pytest.mark.asyncio
async def test_get_job_status(client: AsyncClient):
    with patch("app.services.queue.get_job_status") as mock_status:
        mock_status.return_value = {"status": "completed", "result": {}}

        response = await client.get("/api/v1/scripts/jobs/job-123/status")
        assert response.status_code == 200
        mock_status.assert_called_once_with("job-123")
