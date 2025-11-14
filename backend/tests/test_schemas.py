import pytest
from pydantic import ValidationError
from app.schemas.script import ScriptCreate, ScriptResponse


def test_script_create_valid():
    data = {"title": "Test Script", "content": "INT. HOUSE - DAY"}
    script = ScriptCreate(**data)
    assert script.title == "Test Script"
    assert script.content == "INT. HOUSE - DAY"


def test_script_create_empty_title():
    data = {"title": "", "content": "INT. HOUSE - DAY"}
    with pytest.raises(ValidationError):
        ScriptCreate(**data)


def test_script_create_short_content():
    data = {"title": "Test", "content": "x"}
    with pytest.raises(ValidationError):
        ScriptCreate(**data)


def test_script_create_missing_content():
    data = {"title": "Test"}
    with pytest.raises(ValidationError):
        ScriptCreate(**data)


def test_script_response_valid():
    data = {
        "id": 1,
        "title": "Test",
        "predicted_rating": None,
        "total_scenes": None,
        "created_at": "2024-01-01T00:00:00",
    }
    script = ScriptResponse(**data)
    assert script.id == 1
    assert script.predicted_rating is None


def test_script_response_with_rating():
    data = {
        "id": 1,
        "title": "Test",
        "predicted_rating": "PG-13",
        "total_scenes": 10,
        "created_at": "2024-01-01T00:00:00",
    }
    script = ScriptResponse(**data)
    assert script.predicted_rating == "PG-13"
    assert script.total_scenes == 10
