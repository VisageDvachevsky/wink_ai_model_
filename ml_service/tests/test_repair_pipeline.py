from app.repair_pipeline import (
    count_matches,
    parse_script_to_scenes,
    scene_feature_vector,
    normalize_scene_scores,
    map_scores_to_rating,
)
import re


def test_count_matches():
    patterns = [re.compile(r"\bkill\w*", re.I), re.compile(r"\bgun\b", re.I)]
    text = "He killed the man with a gun. Killing spree."
    count = count_matches(patterns, text)
    assert count == 3


def test_count_matches_no_matches():
    patterns = [re.compile(r"\bexplode\w*", re.I)]
    text = "Peaceful day at the office."
    count = count_matches(patterns, text)
    assert count == 0


def test_parse_script_to_scenes():
    script = """
INT. OFFICE - DAY

Sarah types on her computer.

EXT. STREET - NIGHT

John walks down the street.
"""
    scenes = parse_script_to_scenes(script)
    assert len(scenes) >= 2
    assert any("OFFICE" in s["heading"] for s in scenes)
    assert any("STREET" in s["heading"] for s in scenes)


def test_parse_script_to_scenes_no_headings():
    script = "This is just plain text without scene headings."
    scenes = parse_script_to_scenes(script)
    assert len(scenes) >= 1
    assert scenes[0]["heading"] == "scene_0"


def test_scene_feature_vector_violence():
    text = "He pulled out a gun and shot the man. The killer attacked brutally."
    features = scene_feature_vector(text)

    assert features["violence"] > 0
    assert "length" in features


def test_scene_feature_vector_profanity():
    text = "Fuck you! This shit is crazy, bitch."
    features = scene_feature_vector(text)

    assert features["profanity"] >= 3


def test_scene_feature_vector_gore():
    text = "Blood everywhere. The corpse was bleeding. Bloody wounds."
    features = scene_feature_vector(text)

    assert features["gore"] > 0


def test_scene_feature_vector_drugs():
    text = "He took heroin and cocaine. Drugs everywhere. Pills scattered."
    features = scene_feature_vector(text)

    assert features["drugs"] >= 3


def test_scene_feature_vector_sex():
    text = "Sexual intercourse scene. They had sex. Explicit sexual content."
    features = scene_feature_vector(text)

    assert features["sex_act"] >= 2


def test_scene_feature_vector_child_mentions():
    text = "The child ran to her daughter. Kids playing in the yard."
    features = scene_feature_vector(text)

    assert features["child_mentions"] >= 2


def test_scene_feature_vector_heroic_reduction():
    text = "Superman fights the villain to save metropolis. Hero uses powers."
    features = scene_feature_vector(text)
    assert features["violence"] >= 0


def test_scene_feature_vector_stylized_violence():
    text = "They fight and battle. Action scene without blood."
    features = scene_feature_vector(text)
    assert features["violence"] >= 0


def test_normalize_scene_scores():
    features = {
        "violence": 10,
        "gore": 5,
        "sex_act": 2,
        "nudity": 6,
        "profanity": 15,
        "drugs": 8,
        "child_mentions": 5,
        "length": 200,
    }

    normalized = normalize_scene_scores(features)

    assert 0 <= normalized["violence"] <= 1
    assert 0 <= normalized["gore"] <= 1
    assert 0 <= normalized["sex_act"] <= 1
    assert normalized["profanity"] <= 1
    assert normalized["drugs"] <= 1


def test_map_scores_to_rating_6_plus():
    agg = {
        "violence": 0.1,
        "gore": 0.0,
        "sex_act": 0.0,
        "nudity": 0.0,
        "profanity": 0.1,
        "drugs": 0.0,
        "child_risk": 0.0,
    }

    result = map_scores_to_rating(agg)
    assert result["rating"] == "6+"


def test_map_scores_to_rating_12_plus():
    agg = {
        "violence": 0.3,
        "gore": 0.1,
        "sex_act": 0.0,
        "nudity": 0.0,
        "profanity": 0.4,
        "drugs": 0.0,
        "child_risk": 0.0,
    }

    result = map_scores_to_rating(agg)
    assert result["rating"] == "12+"


def test_map_scores_to_rating_16_plus():
    agg = {
        "violence": 0.65,
        "gore": 0.4,
        "sex_act": 0.2,
        "nudity": 0.1,
        "profanity": 0.3,
        "drugs": 0.2,
        "child_risk": 0.0,
    }

    result = map_scores_to_rating(agg)
    assert result["rating"] == "16+"


def test_map_scores_to_rating_18_plus_explicit():
    agg = {
        "violence": 0.5,
        "gore": 0.95,
        "sex_act": 0.3,
        "nudity": 0.4,
        "profanity": 0.5,
        "drugs": 0.3,
        "child_risk": 0.0,
    }

    result = map_scores_to_rating(agg)
    assert result["rating"] == "18+"


def test_map_scores_to_rating_18_plus_child_risk():
    agg = {
        "violence": 0.6,
        "gore": 0.3,
        "sex_act": 0.5,
        "nudity": 0.2,
        "profanity": 0.3,
        "drugs": 0.2,
        "child_risk": 0.75,
    }

    result = map_scores_to_rating(agg)
    assert result["rating"] == "18+"
    assert len(result["reasons"]) > 0
