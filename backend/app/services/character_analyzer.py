import re
from typing import List, Dict, Any, Set
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class CharacterStats:
    name: str
    profanity_count: int
    violence_scenes: int
    sex_scenes: int
    drug_scenes: int
    total_problematic_scenes: int
    severity_score: float
    scene_appearances: Dict[int, List[str]]
    recommendations: List[str]


class CharacterAnalyzer:
    CHARACTER_PATTERNS = [
        r"^([A-ZА-ЯЁ][A-ZА-ЯЁ\s]+):",
        r"^([A-ZА-ЯЁ][A-ZА-ЯЁ\s]+)\s*\(",
    ]

    @classmethod
    def extract_characters(cls, script_text: str) -> Set[str]:
        characters = set()
        lines = script_text.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            for pattern in cls.CHARACTER_PATTERNS:
                match = re.match(pattern, line)
                if match:
                    char_name = match.group(1).strip()
                    if len(char_name) >= 2 and char_name.isupper():
                        characters.add(char_name)

        return characters

    @classmethod
    def analyze_characters(
        cls,
        script_text: str,
        line_findings: List[Any] = None,
        scenes: List[Any] = None,
    ) -> List[CharacterStats]:
        characters = cls.extract_characters(script_text)
        lines = script_text.split("\n")

        character_stats: Dict[str, CharacterStats] = {}

        for char_name in characters:
            stats = cls._analyze_character(
                char_name, lines, line_findings or [], scenes or []
            )
            character_stats[char_name] = stats

        results = sorted(
            character_stats.values(), key=lambda x: x.severity_score, reverse=True
        )

        return results

    @classmethod
    def _analyze_character(
        cls,
        char_name: str,
        lines: List[str],
        line_findings: List[Any],
        scenes: List[Any],
    ) -> CharacterStats:
        profanity_count = 0
        violence_scenes = 0
        sex_scenes = 0
        drug_scenes = 0
        scene_appearances: Dict[int, List[str]] = defaultdict(list)
        current_scene = 0

        profanity_pattern = re.compile(
            r"\b(?:бля(?:ть|дь|)|хуй|пизд[аеыяоу]|ебать|ёб|съеб|уеб|наеб|еба(?:ть|л|н)|хер|мудак|мудил|гандон|говн[оыа]|пидор|сука|блять|fuck|shit|damn|bitch|ass(?:hole)?|dick|cock|cunt)\b",
            re.IGNORECASE | re.UNICODE,
        )

        violence_keywords = [
            "убив",
            "убий",
            "бить",
            "удар",
            "драк",
            "резать",
            "застрел",
            "kill",
            "murder",
            "hit",
            "shoot",
        ]
        sex_keywords = ["секс", "траха", "sex", "fuck", "intercourse"]
        drug_keywords = [
            "наркотик",
            "кокаин",
            "героин",
            "марихуан",
            "drug",
            "cocaine",
            "heroin",
        ]

        in_character_dialogue = False
        dialogue_buffer = []

        for line_idx, line in enumerate(lines):
            line_stripped = line.strip()

            if re.match(r"^(?:INT\.|EXT\.|FADE)", line_stripped, re.IGNORECASE):
                current_scene += 1

            if line_stripped.startswith(char_name + ":") or line_stripped.startswith(
                char_name + " ("
            ):
                in_character_dialogue = True
                dialogue_buffer = [line_stripped]
                continue

            if in_character_dialogue:
                if line_stripped and not line_stripped[0].isupper():
                    dialogue_buffer.append(line_stripped)
                else:
                    dialogue_text = " ".join(dialogue_buffer)

                    profanity_matches = profanity_pattern.findall(dialogue_text)
                    profanity_count += len(profanity_matches)

                    if any(kw in dialogue_text.lower() for kw in violence_keywords):
                        violence_scenes += 1
                        scene_appearances[current_scene].append("violence")

                    if any(kw in dialogue_text.lower() for kw in sex_keywords):
                        sex_scenes += 1
                        scene_appearances[current_scene].append("sex")

                    if any(kw in dialogue_text.lower() for kw in drug_keywords):
                        drug_scenes += 1
                        scene_appearances[current_scene].append("drugs")

                    if profanity_matches:
                        scene_appearances[current_scene].append("profanity")

                    in_character_dialogue = False
                    dialogue_buffer = []

            if char_name in line_stripped:
                if current_scene not in scene_appearances:
                    scene_appearances[current_scene].append("appearance")

        scene_appearances_dict = {k: list(set(v)) for k, v in scene_appearances.items()}

        total_problematic = len(
            [
                s
                for s, tags in scene_appearances_dict.items()
                if any(tag in ["violence", "sex", "drugs", "profanity"] for tag in tags)
            ]
        )

        severity_score = (
            profanity_count * 0.1
            + violence_scenes * 0.3
            + sex_scenes * 0.4
            + drug_scenes * 0.3
        )

        recommendations = cls._generate_recommendations(
            char_name,
            profanity_count,
            violence_scenes,
            sex_scenes,
            drug_scenes,
        )

        return CharacterStats(
            name=char_name,
            profanity_count=profanity_count,
            violence_scenes=violence_scenes,
            sex_scenes=sex_scenes,
            drug_scenes=drug_scenes,
            total_problematic_scenes=total_problematic,
            severity_score=severity_score,
            scene_appearances=scene_appearances_dict,
            recommendations=recommendations,
        )

    @classmethod
    def _generate_recommendations(
        cls,
        char_name: str,
        profanity_count: int,
        violence_scenes: int,
        sex_scenes: int,
        drug_scenes: int,
    ) -> List[str]:
        recommendations = []

        if profanity_count > 10:
            recommendations.append(
                f"Reduce profanity for {char_name} ({profanity_count} instances)"
            )
        elif profanity_count > 5:
            recommendations.append(
                f"Consider softening language for {char_name} ({profanity_count} instances)"
            )

        if violence_scenes > 3:
            recommendations.append(
                f"Reduce violent scenes involving {char_name} ({violence_scenes} scenes)"
            )

        if sex_scenes > 1:
            recommendations.append(
                f"Consider reducing sexual content for {char_name} ({sex_scenes} scenes)"
            )

        if drug_scenes > 2:
            recommendations.append(
                f"Reduce drug-related scenes for {char_name} ({drug_scenes} scenes)"
            )

        if not recommendations:
            recommendations.append(f"{char_name} has minimal problematic content")

        return recommendations

    @classmethod
    def get_top_offenders(
        cls, character_stats: List[CharacterStats], limit: int = 5
    ) -> List[CharacterStats]:
        return sorted(character_stats, key=lambda x: x.severity_score, reverse=True)[
            :limit
        ]
