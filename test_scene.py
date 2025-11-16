#!/usr/bin/env python3
"""Test script to reproduce the rating issue with the children's adventure scene."""

import sys
sys.path.insert(0, 'ml_service/app')

from repair_pipeline import (
    extract_scene_features,
    normalize_and_contextualize_scores,
    GORE_WORDS,
    count_pattern_matches
)

# Проблемная сцена
scene_text = """EXT. ВЫХОД ИЗ ПЕЩЕРЫ - ДЕНЬ

Дети выбираются из пещеры после того, как НЕЗНАКОМЕЦ уходит
вглубь.

ЛЁША
Надо сообщить взрослым!

СОНЯ
Но у нас нет доказательств! Нам не
поверят, скажут, что мы
фантазируем.

ЛЁША
(решительно)
Тогда нам нужно найти этот клад
раньше него! Смотри на карту -
дедушка нарисовал тут какой-то
крестик."""

print("=" * 70)
print("Testing problematic scene from children's adventure script")
print("=" * 70)
print(f"\nScene text:\n{scene_text}\n")

# Check for gore keyword matches
print("=" * 70)
print("GORE KEYWORD ANALYSIS")
print("=" * 70)
gore_count, gore_excerpts = count_pattern_matches(GORE_WORDS, scene_text.lower())
print(f"Gore keyword count: {gore_count}")
print(f"Gore excerpts: {gore_excerpts}\n")

# Extract full features
print("=" * 70)
print("FULL FEATURE EXTRACTION")
print("=" * 70)
features = extract_scene_features(scene_text)
print(f"Violence count: {features['violence_count']}")
print(f"Gore count: {features['gore_count']}")
print(f"Sex count: {features['sex_count']}")
print(f"Profanity count: {features['profanity_count']}")
print(f"Drugs count: {features['drugs_count']}")
print(f"Scene length (words): {features['length']}\n")

# Normalize scores
print("=" * 70)
print("NORMALIZED SCORES")
print("=" * 70)
normalized = normalize_and_contextualize_scores(features)
print(f"Violence score: {normalized['violence']:.2%}")
print(f"Gore score: {normalized['gore']:.2%}")
print(f"Sex score: {normalized['sex_act']:.2%}")
print(f"Profanity score: {normalized['profanity']:.2%}")
print(f"Drugs score: {normalized['drugs']:.2%}")
print(f"Child risk score: {normalized['child_risk']:.2%}\n")

print("=" * 70)
print("CONTEXT SCORES")
print("=" * 70)
for ctx_type, score in normalized['context_scores'].items():
    if score > 0.4:
        print(f"{ctx_type}: {score:.2%}")
print("\n")

# Expected: all scores should be close to 0 for a children's adventure scene
if normalized['gore'] > 0.5:
    print("❌ BUG CONFIRMED: Gore score is abnormally high!")
    print(f"   Gore score: {normalized['gore']:.2%}")
    print(f"   This is a children's adventure scene with no gore content.")
else:
    print("✅ Scores look normal")
