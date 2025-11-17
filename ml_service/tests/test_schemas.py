import pytest
from pydantic import ValidationError
from ml_service.app.schemas import (
    ScriptRequest,
    SceneFeatures,
    ScriptRatingResponse,
    HealthResponse,
)


def test_script_request_valid():
    request = ScriptRequest(
        script_id="test123", text="INT. OFFICE - DAY\n\nSarah types on her computer."
    )
    assert request.script_id == "test123"
    assert "OFFICE" in request.text


def test_script_request_without_id():
    request = ScriptRequest(text="INT. ROOM - DAY\n\nJohn enters the room.")
    assert request.script_id is None
    assert request.text is not None


def test_script_request_text_too_short():
    with pytest.raises(ValidationError):
        ScriptRequest(text="Too short")


def test_scene_features_valid():
    scene = SceneFeatures(
        scene_id=1,
        heading="INT. OFFICE - DAY",
        violence=0.5,
        gore=0.2,
        sex_act=0.0,
        nudity=0.0,
        profanity=0.3,
        drugs=0.0,
        child_risk=0.0,
        weight=0.8,
    )
    assert scene.violence == 0.5
    assert scene.weight == 0.8


def test_scene_features_values_out_of_range():
    with pytest.raises(ValidationError):
        SceneFeatures(
            scene_id=1,
            heading="INT. OFFICE - DAY",
            violence=1.5,
            gore=0.0,
            sex_act=0.0,
            nudity=0.0,
            profanity=0.0,
            drugs=0.0,
            child_risk=0.0,
            weight=0.5,
        )


def test_script_rating_response_valid():
    response = ScriptRatingResponse(
        script_id="test123",
        predicted_rating="12+",
        reasons=["Mild violence"],
        agg_scores={"violence": 0.3},
        top_trigger_scenes=[],
        model_version="v1.0",
        total_scenes=5,
    )
    assert response.predicted_rating == "12+"
    assert response.total_scenes == 5


def test_script_rating_response_invalid_rating():
    with pytest.raises(ValidationError):
        ScriptRatingResponse(
            script_id="test123",
            predicted_rating="15+",
            reasons=[],
            agg_scores={},
            top_trigger_scenes=[],
            model_version="v1.0",
            total_scenes=1,
        )


def test_health_response():
    health = HealthResponse(status="healthy", model_version="v1.0", model_loaded=True)
    assert health.status == "healthy"
    assert health.model_loaded is True
