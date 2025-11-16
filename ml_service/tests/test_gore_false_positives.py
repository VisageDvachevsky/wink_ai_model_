"""
Test suite for gore pattern false positive detection.

This test ensures that common Russian words are not incorrectly flagged as gore content.

Issue: The pattern r"\bран\w+" was matching "раньше" (earlier) and flagging
innocent children's adventure scenes as having 100% gore content.

Fix: Changed patterns to be more specific and added false positive filters.
"""

import re


# Gore patterns (updated)
GORE_WORDS = [
    r"\bкровь\b",
    r"\bкров[ьи]ю\b",
    r"\bкровав\w*",
    r"\bкровоточ\w*",
    r"\bран(?:а|ы|у|ой|е|ам|ами|ах)\b",  # Only wound forms
    r"\bмозг(?:и|ов|у|ом|ах|ами)?\b",
]

# False positive filters
FALSE_POSITIVES = [
    r"кроват\w*",  # bed
    r"\bкров[ао](?:м|й|ю|е|й|и)?\b",  # shelter
    r"мозгов(ой|ым|ого|ому|ая|ую)\s+(штурм|центр|атак|трест)",  # brainstorm etc
    r"ран(ь|н)(ше|ий|яя|ее|его|им|ему)",  # earlier, early
]


def has_gore_match(text):
    """Check if text has gore content after filtering false positives."""
    false_positive_patterns = [re.compile(p, re.I) for p in FALSE_POSITIVES]

    for pattern in GORE_WORDS:
        regex = re.compile(pattern, re.I)
        for match in regex.finditer(text.lower()):
            # Extract context
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            excerpt = text[start:end].strip()

            # Check if it's a false positive
            is_false_positive = any(
                fp.search(excerpt) for fp in false_positive_patterns
            )

            if not is_false_positive:
                return True, excerpt

    return False, None


class TestGoreFalsePositives:
    """Test cases for gore false positive detection."""

    def test_earlier_not_flagged_as_gore(self):
        """Word 'раньше' (earlier) should NOT be flagged as gore."""
        text = "Нам нужно найти клад раньше него!"
        has_gore, excerpt = has_gore_match(text)
        assert not has_gore, f"'раньше' incorrectly flagged as gore: {excerpt}"

    def test_early_not_flagged_as_gore(self):
        """Word 'ранний' (early) should NOT be flagged as gore."""
        text = "Ранний утром они отправились в путь"
        has_gore, excerpt = has_gore_match(text)
        assert not has_gore, f"'ранний' incorrectly flagged as gore: {excerpt}"

    def test_bed_not_flagged_as_gore(self):
        """Word 'кровать' (bed) should NOT be flagged as gore."""
        text = "Он лег на кровать и заснул"
        has_gore, excerpt = has_gore_match(text)
        assert not has_gore, f"'кровать' incorrectly flagged as gore: {excerpt}"

    def test_shelter_not_flagged_as_gore(self):
        """Word 'крова' (shelter) should NOT be flagged as gore."""
        text = "Путники искали крова на ночь"
        has_gore, excerpt = has_gore_match(text)
        assert not has_gore, f"'крова' incorrectly flagged as gore: {excerpt}"

    def test_brainstorm_not_flagged_as_gore(self):
        """Phrase 'мозговой штурм' (brainstorm) should NOT be flagged as gore."""
        text = "Они устроили мозговой штурм"
        has_gore, excerpt = has_gore_match(text)
        assert not has_gore, f"'мозговой штурм' incorrectly flagged as gore: {excerpt}"

    def test_wound_is_flagged_as_gore(self):
        """Word 'рана' (wound) SHOULD be flagged as gore."""
        text = "На его теле была глубокая рана"
        has_gore, excerpt = has_gore_match(text)
        assert has_gore, "'рана' should be flagged as gore"

    def test_blood_is_flagged_as_gore(self):
        """Word 'кровь' (blood) SHOULD be flagged as gore."""
        text = "Кровь текла из раны"
        has_gore, excerpt = has_gore_match(text)
        assert has_gore, "'кровь' should be flagged as gore"

    def test_bloody_is_flagged_as_gore(self):
        """Word 'кровавый' (bloody) SHOULD be flagged as gore."""
        text = "Это была кровавая битва"
        has_gore, excerpt = has_gore_match(text)
        assert has_gore, "'кровавый' should be flagged as gore"

    def test_childrens_adventure_scene(self):
        """
        Real-world test: children's adventure scene should have no gore.

        This is the actual scene that triggered the bug report.
        """
        scene = """
        EXT. ВЫХОД ИЗ ПЕЩЕРЫ - ДЕНЬ

        Дети выбираются из пещеры после того, как НЕЗНАКОМЕЦ уходит вглубь.

        ЛЁША
        Надо сообщить взрослым!

        СОНЯ
        Но у нас нет доказательств! Нам не поверят, скажут, что мы фантазируем.

        ЛЁША
        (решительно)
        Тогда нам нужно найти этот клад раньше него! Смотри на карту -
        дедушка нарисовал тут какой-то крестик.
        """

        has_gore, excerpt = has_gore_match(scene)
        assert not has_gore, f"Children's adventure scene incorrectly flagged as gore: {excerpt}"


if __name__ == "__main__":
    # Run tests
    test = TestGoreFalsePositives()

    print("Running gore false positive tests...")
    print("=" * 70)

    tests = [
        ("earlier not flagged", test.test_earlier_not_flagged_as_gore),
        ("early not flagged", test.test_early_not_flagged_as_gore),
        ("bed not flagged", test.test_bed_not_flagged_as_gore),
        ("shelter not flagged", test.test_shelter_not_flagged_as_gore),
        ("brainstorm not flagged", test.test_brainstorm_not_flagged_as_gore),
        ("wound IS flagged", test.test_wound_is_flagged_as_gore),
        ("blood IS flagged", test.test_blood_is_flagged_as_gore),
        ("bloody IS flagged", test.test_bloody_is_flagged_as_gore),
        ("children's adventure scene", test.test_childrens_adventure_scene),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            print(f"✅ {name}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {name}: {e}")
            failed += 1

    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
        exit(1)
