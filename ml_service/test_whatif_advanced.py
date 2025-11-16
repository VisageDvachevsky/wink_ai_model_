#!/usr/bin/env python3
"""
Test script for Advanced What-If Analyzer.
Demonstrates reducing an 18+ rated script to 16+.
"""
import json
import requests
from pathlib import Path

ML_SERVICE_URL = "http://localhost:8001"


def load_script(filepath: str) -> str:
    """Load script from file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def load_request_template(filepath: str) -> dict:
    """Load request template from JSON."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze_original(script_text: str) -> dict:
    """Get original rating."""
    response = requests.post(
        f"{ML_SERVICE_URL}/rate_script",
        json={"text": script_text, "script_id": "test-18plus"},
    )
    response.raise_for_status()
    return response.json()


def analyze_whatif(request_data: dict) -> dict:
    """Run advanced what-if analysis."""
    response = requests.post(f"{ML_SERVICE_URL}/what_if_advanced", json=request_data)
    response.raise_for_status()
    return response.json()


def print_results(original: dict, whatif_result: dict):
    """Print analysis results."""
    print("\n" + "=" * 80)
    print("ADVANCED WHAT-IF ANALYSIS RESULTS")
    print("=" * 80)

    print("\n📊 ORIGINAL ANALYSIS:")
    print(f"  Rating: {original.get('predicted_rating', 'N/A')}")
    print(f"  Total Scenes: {original.get('total_scenes', 'N/A')}")

    if "agg_scores" in original:
        print("\n  Scores:")
        for key, value in original["agg_scores"].items():
            print(f"    - {key}: {value:.3f}")

    print("\n  Reasons:")
    for reason in original.get("reasons", []):
        print(f"    • {reason}")

    print("\n" + "-" * 80)

    print("\n🔧 WHAT-IF MODIFICATIONS:")
    print(f"  Original Rating: {whatif_result['original_rating']}")
    print(f"  Modified Rating: {whatif_result['modified_rating']}")
    print(
        f"  Rating Changed: {'✅ YES' if whatif_result['rating_changed'] else '❌ NO'}"
    )

    print("\n  Applied Modifications:")
    for i, mod in enumerate(whatif_result["modifications_applied"], 1):
        print(f"    {i}. {mod['type']}")
        if "metadata" in mod:
            for key, val in mod["metadata"].items():
                if isinstance(val, (int, float, str)):
                    print(f"       - {key}: {val}")

    print("\n📈 SCORE CHANGES:")
    orig_scores = whatif_result["original_scores"]
    mod_scores = whatif_result["modified_scores"]

    for key in orig_scores:
        orig = orig_scores[key]
        mod = mod_scores[key]
        diff = mod - orig
        arrow = "↓" if diff < 0 else "↑" if diff > 0 else "→"
        print(f"    {key:15s}: {orig:.3f} → {mod:.3f}  {arrow} {abs(diff):.3f}")

    print("\n💡 EXPLANATION:")
    print(f"  {whatif_result['explanation']}")

    print("\n👥 ENTITIES EXTRACTED:")
    entities_by_type = {}
    for entity in whatif_result["entities_extracted"][:15]:
        etype = entity["type"]
        if etype not in entities_by_type:
            entities_by_type[etype] = []
        entities_by_type[etype].append(entity)

    for etype, entities in entities_by_type.items():
        print(f"\n  {etype.capitalize()}s:")
        for entity in entities[:5]:
            print(
                f"    • {entity['name']} ({entity['mentions']} mentions in scenes {entity['scenes'][:3]}...)"
            )

    print("\n🎬 SCENE ANALYSIS:")
    scene_type_counts = {}
    for scene in whatif_result["scene_analysis"]:
        stype = scene["scene_type"]
        scene_type_counts[stype] = scene_type_counts.get(stype, 0) + 1

    print(f"  Total Scenes: {len(whatif_result['scene_analysis'])}")
    print("  Scene Types:")
    for stype, count in sorted(
        scene_type_counts.items(), key=lambda x: x[1], reverse=True
    ):
        print(f"    • {stype}: {count}")

    print("\n" + "=" * 80)

    if whatif_result.get("modified_script"):
        print("\n📝 MODIFIED SCRIPT (first 500 chars):")
        print("-" * 80)
        print(whatif_result["modified_script"][:500])
        print("...")
        print("-" * 80)


def main():
    script_dir = Path(__file__).parent

    print("🎬 Loading 18+ rated script...")
    script_text = load_script(script_dir / "test_script_18plus.txt")
    print(f"   Script length: {len(script_text)} characters")
    print(f"   Word count: ~{len(script_text.split())} words")

    print("\n📊 Analyzing original script...")
    try:
        original = analyze_original(script_text)
        print(f"   ✅ Original rating: {original.get('predicted_rating', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return

    print("\n🔧 Loading what-if modifications...")
    request_template = load_request_template(script_dir / "test_whatif_request.json")
    request_template["script_text"] = script_text

    print(f"   Modifications to apply: {len(request_template['modifications'])}")
    for mod in request_template["modifications"]:
        print(f"     - {mod['type']}")

    print("\n⚙️  Running advanced what-if analysis...")
    try:
        whatif_result = analyze_whatif(request_template)
        print("   ✅ Analysis complete!")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return

    print_results(original, whatif_result)

    print("\n" + "=" * 80)
    print("🎯 GOAL CHECK:")
    original_rating = whatif_result["original_rating"]
    modified_rating = whatif_result["modified_rating"]

    if original_rating == "18+" and modified_rating in ["16+", "12+"]:
        print("   ✅ SUCCESS! Rating reduced from 18+ to", modified_rating)
    elif original_rating == "18+" and modified_rating == "18+":
        print("   ⚠️  PARTIAL: Rating still 18+, need more aggressive modifications")
    else:
        print(f"   ℹ️  Rating: {original_rating} → {modified_rating}")

    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
