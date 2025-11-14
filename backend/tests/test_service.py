import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch
from app.services.script_service import script_service
from app.schemas.script import ScriptCreate
from app.models.script import Script
from app.core.exceptions import ScriptNotFoundError


@pytest.mark.asyncio
async def test_create_script_service(test_session: AsyncSession):
    script_data = ScriptCreate(
        title="Service Test", content="INT. ROOM - DAY\n\nAction happens."
    )

    script = await script_service.create_script(test_session, script_data)

    assert script.id is not None
    assert script.title == "Service Test"
    assert script.content == "INT. ROOM - DAY\n\nAction happens."


@pytest.mark.asyncio
async def test_get_script_service(test_session: AsyncSession, sample_script: Script):
    script = await script_service.get_script(test_session, sample_script.id)

    assert script is not None
    assert script.id == sample_script.id
    assert script.title == sample_script.title


@pytest.mark.asyncio
async def test_get_nonexistent_script_service(test_session: AsyncSession):
    script = await script_service.get_script(test_session, 99999)
    assert script is None


@pytest.mark.asyncio
async def test_list_scripts_service(test_session: AsyncSession, sample_script: Script):
    scripts = await script_service.list_scripts(test_session, skip=0, limit=10)

    assert len(scripts) >= 1
    assert any(s.id == sample_script.id for s in scripts)


@pytest.mark.asyncio
async def test_list_scripts_with_skip(test_session: AsyncSession):
    for i in range(5):
        script_data = ScriptCreate(title=f"Script {i}", content="Content")
        await script_service.create_script(test_session, script_data)

    scripts = await script_service.list_scripts(test_session, skip=2, limit=2)
    assert len(scripts) == 2


@pytest.mark.asyncio
async def test_process_rating_not_found(test_session: AsyncSession):
    with pytest.raises(ScriptNotFoundError):
        await script_service.process_rating(test_session, 99999)


@pytest.mark.asyncio
async def test_process_rating_success(test_session: AsyncSession, sample_script: Script):
    mock_result = {
        "predicted_rating": "PG",
        "agg_scores": {"violence": 0.1},
        "model_version": "v1.0",
        "total_scenes": 3,
        "top_trigger_scenes": [
            {
                "scene_id": 1,
                "heading": "INT. OFFICE - DAY",
                "violence": 0.1,
                "gore": 0.0,
                "sex_act": 0.0,
                "nudity": 0.0,
                "profanity": 0.0,
                "drugs": 0.0,
                "child_risk": 0.0,
                "weight": 0.1,
            }
        ],
        "reasons": ["Minimal content"],
    }

    with patch("app.services.ml_client.ml_client.rate_script") as mock_rate:
        mock_rate.return_value = mock_result

        result = await script_service.process_rating(
            test_session, sample_script.id
        )

        assert result["predicted_rating"] == "PG"
        assert result["total_scenes"] == 3

        updated_script = await script_service.get_script(
            test_session, sample_script.id
        )
        assert updated_script.predicted_rating == "PG"
        assert len(updated_script.scenes) == 1


@pytest.mark.asyncio
async def test_process_rating_rollback_on_error(
    test_session: AsyncSession, sample_script: Script
):
    with patch("app.services.ml_client.ml_client.rate_script") as mock_rate:
        mock_rate.side_effect = Exception("ML service error")

        with pytest.raises(Exception):
            await script_service.process_rating(test_session, sample_script.id)

        script = await script_service.get_script(test_session, sample_script.id)
        assert script.predicted_rating is None
