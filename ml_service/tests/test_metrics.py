import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_metrics_endpoint_exists(client):
    response = client.get("/metrics")
    assert response.status_code == 200


def test_metrics_format(client):
    response = client.get("/metrics")
    content = response.text

    assert "rating_inference_duration_seconds" in content
    assert "rating_requests_total" in content
    assert "rating_errors_total" in content


def test_metrics_updated_after_request(client):
    metrics_before = client.get("/metrics").text

    payload = {"text": "INT. HOUSE - DAY\n\nSimple scene."}
    client.post("/rate_script", json=payload)

    metrics_after = client.get("/metrics").text
    assert metrics_after != metrics_before


def test_metrics_track_errors(client):
    metrics_before = client.get("/metrics").text

    payload = {"text": ""}
    response = client.post("/rate_script", json=payload)
    assert response.status_code == 422

    metrics_after = client.get("/metrics").text
    assert "rating_errors_total" in metrics_after
