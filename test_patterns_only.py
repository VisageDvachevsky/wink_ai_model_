#!/usr/bin/env python3
"""Test just the pattern matching logic without loading the full model."""

import re

# Updated GORE patterns (from repair_pipeline.py)
GORE_WORDS = [
    r"\bкровь\b",
    r"\bкров[ьи]ю\b",
    r"\bкровав\w*",
    r"\bкровоточ\w*",
    r"\bран(?:а|ы|у|ой|е|ам|ами|ах)\b",
]

# Updated FALSE_POSITIVES
FALSE_POSITIVES = [
    r"кроват\w*",
    r"\bкров[ао](?:м|й|ю|е|й|и)?\b",
    r"ран(ь|н)(ше|ий|яя|ее|его|им|ему)",
]

def count_pattern_matches_simple(patterns, text):
    """Simplified pattern matching with false positive filtering."""
    false_positive_patterns = [re.compile(p, re.I) for p in FALSE_POSITIVES]

    matches = []
    count = 0
    for pattern in patterns:
        regex = re.compile(pattern, re.I)
        found = regex.finditer(text)
        for match in found:
            # Extract context around match
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            excerpt = text[start:end].strip()

            # Check if it's a false positive
            is_false_positive = any(
                fp.search(excerpt) for fp in false_positive_patterns
            )

            if not is_false_positive:
                matches.append(excerpt)
                count += 1

    return count, matches

# Problematic scene
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
print("Testing GORE pattern matching on problematic scene")
print("=" * 70)
print()

gore_count, gore_excerpts = count_pattern_matches_simple(GORE_WORDS, scene_text.lower())

print(f"Scene text preview:")
print(scene_text[:200] + "...")
print()
print(f"GORE matches found: {gore_count}")
print(f"GORE excerpts: {gore_excerpts}")
print()

if gore_count == 0:
    print("✅ SUCCESS! No false positives detected.")
    print("   The scene is correctly identified as having no gore content.")
else:
    print(f"❌ FAILURE! Found {gore_count} gore match(es) in a children's scene.")
    print("   This is a false positive that needs to be fixed.")
