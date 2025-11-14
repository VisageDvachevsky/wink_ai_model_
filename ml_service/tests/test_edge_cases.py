import pytest
from app.pipeline import RatingPipeline


@pytest.fixture
def pipeline():
    return RatingPipeline()


def test_empty_script(pipeline):
    result = pipeline.analyze_script("", script_id="empty")
    assert result["total_scenes"] == 0
    assert result["predicted_rating"] == "6+"


def test_very_long_script(pipeline):
    long_script = "INT. HOUSE - DAY\n\n" + ("Action happens. " * 10000)
    result = pipeline.analyze_script(long_script, script_id="long")
    assert result["total_scenes"] > 0
    assert len(result["top_trigger_scenes"]) <= 10


def test_script_with_only_headings(pipeline):
    script = "INT. HOUSE - DAY\n\nEXT. STREET - NIGHT\n\nINT. OFFICE - DAY"
    result = pipeline.analyze_script(script, script_id="headings")
    assert result["total_scenes"] >= 3


def test_script_with_unicode(pipeline):
    script = "INT. CAFÉ - DAY\n\nJean-Pierre parle français. Здравствуй мир."
    result = pipeline.analyze_script(script, script_id="unicode")
    assert result["predicted_rating"] is not None


def test_profanity_detection(pipeline):
    scene_text = "Fuck this shit. Damn it all to hell. Motherfucker."
    features = pipeline.scene_feature_vector(scene_text)
    assert features["profanity"] > 3


def test_drug_detection(pipeline):
    scene_text = "He injected heroin. Cocaine on the table. Smoking marijuana."
    features = pipeline.scene_feature_vector(scene_text)
    assert features["drugs"] > 2


def test_child_risk_detection(pipeline):
    scene_text = "The child was hurt. Kid in danger. Minor at risk."
    features = pipeline.scene_feature_vector(scene_text)
    normalized = pipeline.normalize_scene_scores(features)
    assert normalized["child_risk"] > 0


def test_heroic_violence_reduction(pipeline):
    script_superhero = """
    INT. GOTHAM - NIGHT

    Batman fights the villain. Superman saves the day.
    Violence happens but heroes win.
    """

    script_regular = """
    INT. STREET - NIGHT

    Man fights another man. Violence happens. Someone loses.
    """

    result_hero = pipeline.analyze_script(script_superhero, script_id="hero")
    result_regular = pipeline.analyze_script(script_regular, script_id="regular")

    assert result_hero["agg_scores"]["violence"] <= result_regular["agg_scores"]["violence"]


def test_multiple_content_types(pipeline):
    script = """
    INT. DARK ROOM - NIGHT

    Violence, blood, murder. Explicit sex scene with nudity.
    Drug use visible. Profanity: fuck, shit, damn.
    Child present during violent scene.
    """

    result = pipeline.analyze_script(script, script_id="multi")
    assert result["predicted_rating"] == "18+"
    assert result["agg_scores"]["violence"] > 0.5
    assert result["agg_scores"]["sex_act"] > 0.5
    assert result["agg_scores"]["drugs"] > 0


def test_scene_weight_calculation(pipeline):
    script = """
    INT. OFFICE - DAY
    Peaceful scene with no content.

    INT. WAREHOUSE - NIGHT
    Extreme violence, blood, murder, death, killing, shooting, stabbing.
    """

    result = pipeline.analyze_script(script, script_id="weight")
    if len(result["top_trigger_scenes"]) > 0:
        top_scene = result["top_trigger_scenes"][0]
        assert top_scene["weight"] > 0.3


def test_normalize_scene_scores_bounds(pipeline):
    extreme_features = {
        "violence": 1000,
        "gore": 500,
        "sex_act": 200,
        "nudity": 300,
        "profanity": 150,
        "drugs": 100,
        "child_mentions": 50,
        "length": 100,
    }

    normalized = pipeline.normalize_scene_scores(extreme_features)

    for key, value in normalized.items():
        assert value >= 0, f"{key} should be non-negative"
        if key != "child_risk":
            assert value <= 1.0, f"{key} should be <= 1.0"


def test_aggregate_scene_scores_empty(pipeline):
    agg = pipeline.aggregate_scene_scores([])
    assert all(v == 0 for v in agg.values())


def test_aggregate_scene_scores_weighted(pipeline):
    scenes = [
        {
            "violence": 0.8,
            "gore": 0.6,
            "sex_act": 0.2,
            "nudity": 0.1,
            "profanity": 0.5,
            "drugs": 0.3,
            "child_risk": 0.4,
            "weight": 1.0,
        },
        {
            "violence": 0.2,
            "gore": 0.1,
            "sex_act": 0.0,
            "nudity": 0.0,
            "profanity": 0.1,
            "drugs": 0.0,
            "child_risk": 0.0,
            "weight": 0.2,
        },
    ]

    agg = pipeline.aggregate_scene_scores(scenes)
    assert agg["violence"] > 0.5
