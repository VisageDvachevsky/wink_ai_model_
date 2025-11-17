import pytest
from ml_service.app.metrics import MetricsTracker, track_inference_time, get_metrics


def test_metrics_tracker_timer():
    tracker = MetricsTracker()

    tracker.start_timer("test_operation")
    import time

    time.sleep(0.01)
    duration = tracker.end_timer("test_operation")

    assert duration > 0.01
    assert duration < 0.1


def test_metrics_tracker_end_nonexistent_timer():
    tracker = MetricsTracker()
    duration = tracker.end_timer("nonexistent")
    assert duration == 0.0


def test_metrics_tracker_record_scene_parsing():
    tracker = MetricsTracker()
    tracker.record_scene_parsing(0.05)


def test_metrics_tracker_record_feature_extraction():
    tracker = MetricsTracker()
    tracker.record_feature_extraction(0.02)


def test_metrics_tracker_record_scores():
    tracker = MetricsTracker()
    scores = {
        "violence": 0.7,
        "sex_act": 0.3,
        "gore": 0.2,
        "profanity": 0.5,
        "drugs": 0.1,
        "nudity": 0.0,
    }
    tracker.record_scores(scores)


def test_metrics_tracker_record_scenes_count():
    tracker = MetricsTracker()
    tracker.record_scenes_count(25)


def test_metrics_tracker_record_rating():
    tracker = MetricsTracker()
    tracker.record_rating("16+")


@pytest.mark.asyncio
async def test_track_inference_time_decorator_async():
    @track_inference_time("test_endpoint")
    async def async_function():
        return {"result": "success"}

    result = await async_function()
    assert result["result"] == "success"


@pytest.mark.asyncio
async def test_track_inference_time_decorator_with_error():
    @track_inference_time("test_endpoint")
    async def failing_function():
        raise ValueError("Test error")

    with pytest.raises(ValueError):
        await failing_function()


def test_track_inference_time_decorator_sync():
    @track_inference_time("test_sync_endpoint")
    def sync_function():
        return {"result": "sync_success"}

    result = sync_function()
    assert result["result"] == "sync_success"


def test_get_metrics():
    metrics_output = get_metrics()
    assert isinstance(metrics_output, bytes)
    assert len(metrics_output) > 0
