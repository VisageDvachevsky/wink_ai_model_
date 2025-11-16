#!/usr/bin/env python3
"""Test improved rating model on problematic children's adventure scene."""

import sys
sys.path.insert(0, 'ml_service/app')

from repair_pipeline import (
    extract_scene_features,
    normalize_and_contextualize_scores,
    map_scores_to_rating,
)

children_scene = """EXT. ВЫХОД ИЗ ПЕЩЕРЫ - ДЕНЬ

Дети выбираются из пещеры после того, как НЕЗНАКОМЕЦ уходит вглубь.

ЛЁША
Надо сообщить взрослым!

СОНЯ
Но у нас нет доказательств! Нам не поверят, скажут, что мы фантазируем.

ЛЁША
(решительно)
Тогда нам нужно найти этот клад раньше него! Смотри на карту -
дедушка нарисовал тут какой-то крестик."""

violent_scene = """INT. ТЕМНЫЙ ПОДВАЛ - НОЧЬ

Убийца достает нож. ЖЕРТВА кричит. Кровь брызжет на стену.

УБИЙЦА
(зловеще)
Это конец для тебя.

Он наносит множественные удары. Тело падает на пол, истекая кровью.
На полу образуется большая лужа крови."""

discussion_scene = """INT. ПОЛИЦЕЙСКИЙ УЧАСТОК - ДЕНЬ

ДЕТЕКТИВ
Мы нашли следы крови на месте преступления.

СВИДЕТЕЛЬ
Я слышал, что там было много крови.

ДЕТЕКТИВ
Расскажите подробнее о том, что вы видели."""

print("=" * 70)
print("TESTING IMPROVED RATING MODEL")
print("=" * 70)
print()

test_cases = [
    ("Children's Adventure Scene", children_scene, "0+ or 6+"),
    ("Violent Action Scene", violent_scene, "16+ or 18+"),
    ("Discussion Scene", discussion_scene, "12+"),
]

for name, scene_text, expected in test_cases:
    print(f"Test: {name}")
    print(f"Expected rating: {expected}")
    print("-" * 70)

    features = extract_scene_features(scene_text)
    normalized = normalize_and_contextualize_scores(features)

    print(f"Violence: {normalized['violence']:.2%}")
    print(f"Gore: {normalized['gore']:.2%}")
    print(f"Sex: {normalized['sex_act']:.2%}")
    print(f"Profanity: {normalized['profanity']:.2%}")
    print()

    ctx = features['context_scores']
    print("Top context matches:")
    sorted_ctx = sorted(ctx.items(), key=lambda x: x[1], reverse=True)[:3]
    for ctx_type, score in sorted_ctx:
        if score > 0.3:
            print(f"  {ctx_type}: {score:.2%}")

    structure = features.get('structure', {})
    if structure:
        print(f"Dialogue ratio: {structure.get('dialogue_ratio', 0):.2%}")
        print(f"Action weight: {structure.get('action_weight', 1.0):.2f}")

    agg = {
        "violence": normalized['violence'],
        "gore": normalized['gore'],
        "sex_act": normalized['sex_act'],
        "nudity": normalized['nudity'],
        "profanity": normalized['profanity'],
        "drugs": normalized['drugs'],
        "child_risk": normalized.get('child_risk', 0),
        "excerpts": {},
    }

    rating_info = map_scores_to_rating(agg)
    print(f"\nPredicted rating: {rating_info['rating']}")
    print(f"Reasons: {', '.join(rating_info['reasons'])}")
    print("=" * 70)
    print()
