import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

from ..models.script import LineFinding


@dataclass
class LineMatch:
    line_start: int
    line_end: int
    category: str
    severity: float
    matched_text: str
    context_before: List[str]
    context_after: List[str]
    match_count: int
    rating_impact: str


class LineDetector:
    PROFANITY_PATTERNS = [
        r"\bfuck\b",
        r"\bshit\b",
        r"\bmotherfucker\b",
        r"\bbitch\b",
        r"\basshole\b",
        r"\bdamn\b",
        r"\bhell\b",
        r"\bcrap\b",
        r"\bблядь\b",
        r"\bбля\b",
        r"\bсука\b",
        r"\bхуй\b",
        r"\bпизд\w*",
        r"\bебать\b",
        r"\bебал\w*",
        r"\bебан\w*",
        r"\bзаеб\w*",
        r"\bдерьм\w*",
        r"\bговн\w*",
        r"\bхер\w*",
        r"\bмудак\w*",
        r"\bсволоч\w*",
        r"\bтварь\b",
    ]

    VIOLENCE_PATTERNS = [
        r"\bkill\w*",
        r"\bshoot\w*",
        r"\bshot\b",
        r"\bstab\w*",
        r"\bknife\b",
        r"\bgun\w*",
        r"\bpistol\b",
        r"\brifle\b",
        r"\bexplod\w*",
        r"\bblast\w*",
        r"\battack\w*",
        r"\bbeating\b",
        r"\bbeaten\b",
        r"\bbeats\b",
        r"\bcorpse\b",
        r"\bdead\b",
        r"\bmurder\w*",
        r"\bviolence\b",
        r"\bterrorist\b",
        r"\bhostage\b",
        r"\brip(ped|s)? apart\b",
        r"\bthug(s)?\b",
        r"\bterror\b",
        r"\bfight(ing)?\b",
        r"\bbattle(s|d)?\b",
        r"\bwar\b",
        r"\bshoot[- ]?out\b",
        r"\bexplosion\b",
        r"\bgrenade\b",
        r"\bубий\w*",
        r"\bубить\b",
        r"\bубил\w*",
        r"\bубива\w*",
        r"\bстреля\w*",
        r"\bвыстрел\w*",
        r"\bзастрел\w*",
        r"\bзарез\w*",
        r"\bнож\b",
        r"\bоруж\w+",
        r"\bпистолет\w*",
        r"\bвинтовк\w*",
        r"\bавтомат\w*",
        r"\bвзрыв\w*",
        r"\bатак\w*",
        r"\bнападе\w*",
        r"\bизбие\w*",
        r"\bтруп\w*",
        r"\bмертв\w*",
        r"\bпогиб\w*",
        r"\bнасилие\b",
        r"\bжесток\w*",
        r"\bтеррор\w*",
        r"\bзаложник\w*",
        r"\bбандит\w*",
        r"\bдрак\w*",
        r"\bбой\b",
        r"\bсраж\w*",
        r"\bвойна\b",
        r"\bбоев\w*",
        r"\bгранат\w*",
        r"\bбомб\w*",
    ]

    GORE_PATTERNS = [
        r"\bblood\b",
        r"\bbloody\b",
        r"\bbloodied\b",
        r"\bbleeding\b",
        r"\bcorpse\b",
        r"\bwound\b",
        r"\bscar\b",
        r"\binjur\w*",
        r"\bcrash\w*",
        r"\bburn\w*",
        r"\bguts\b",
        r"\bentrails\b",
        r"\bbrain\b",
        r"\bdead body\b",
        r"\bgore\b",
        r"\bmutilat\w*",
        r"\bкровь\b",
        r"\bкров[ьи]ю\b",
        r"\bкровав\w*",
        r"\bкровоточ\w*",
        r"\bран(?:а|ы|у|ой|е|ам|ами|ах)\b",
        r"\bшрам\w*",
        r"\bувечь\w*",
        r"\bожог\w*",
        r"\bкишк\w*",
        r"\bвнутренност\w*",
        r"\bмозг(?:и|ов|у|ом|ах|ами)?\b",
        r"\bрасчленен\w*",
        r"\bизувеч\w*",
    ]

    SEX_PATTERNS = [
        r"\brape\b",
        r"\bsexual\b",
        r"\bintercourse\b",
        r"\bsex scene\b",
        r"\bmolest\b",
        r"\borgasm\b",
        r"\bhaving sex\b",
        r"\bsexually\b",
        r"\bbed\s+scene\b",
        r"\bизнасилов\w*",
        r"\bнасилов\w*",
        r"\bсексуальн\w*",
        r"\bполов\w+\s+акт\w*",
        r"\bинтимн\w*",
        r"\bоргазм\w*",
        r"\bзанимаются\s+сексом\b",
        r"\bзанимались\s+любовью\b",
        r"\bпостельн\w+\s+сцен\w*",
    ]

    NUDITY_PATTERNS = [
        r"\bbra\b",
        r"\bpanty|panties\b",
        r"\bunderwear\b",
        r"\bnaked\b",
        r"\bnude\b",
        r"\bundress\w*",
        r"\btopless\b",
        r"\bголый\b",
        r"\bголая\b",
        r"\bнаг\w*",
        r"\bобнаж\w*",
        r"\bбюстгальтер\w*",
        r"\bтрус\w*",
        r"\bбелье\b",
        r"\bраздева\w*",
        r"\bбез одежд\w*",
    ]

    DRUG_PATTERNS = [
        r"\bdrug(s)?\b",
        r"\bheroin\b",
        r"\bcocaine\b",
        r"\bmarijuana\b",
        r"\bpill(s)?\b",
        r"\bweed\b",
        r"\balcohol\b",
        r"\bdrunk\b",
        r"\bcigarette\b",
        r"\bsmok(e|ing)\b",
        r"\baddiction\b",
        r"\bнаркот\w*",
        r"\bгероин\w*",
        r"\bкокаин\w*",
        r"\bмарихуан\w*",
        r"\bтравк\w*",
        r"\bдоп\w*",
        r"\bтаблетк\w*",
        r"\bпилюл\w*",
        r"\bалкогол\w*",
        r"\bспирт\w*",
        r"\bвыпив\w*",
        r"\bпьян\w*",
        r"\bсигарет\w*",
        r"\bкур\w*",
        r"\bзависим\w*",
        r"\bнакур\w*",
    ]

    CHILD_RISK_PATTERNS = [
        r"\b(?:child(?:ren)?|kid(?:s)?|son|daughter|teen(?:aged)?|boy|girl|minor)\b",
        r"\b(?:ребенок|ребенк\w*|дет\w+|малыш\w*|сын|доч\w*|подросток\w*|мальчик\w*|девочк\w*|несовершеннолетн\w*)\b",
    ]

    FALSE_POSITIVES = [
        r"if (it|that|this) kills",
        r"(it|that|this)\'ll kill",
        r"(it|that|this) (will|would) kill",
        r"gonna.*kill",
        r"kill (you|me|him|her|them|us)",
        r"make love",
        r"kill time",
        r"dressed to kill",
        r"killer instinct",
        r"lady killer",
        r"killing me softly",
        r"shoot the breeze",
        r"shoot for",
        r"shot in the dark",
        r"long shot",
        r"shot at",
        r"light[ -]?shot",
        r"fight (for|to see|to|for the)",
        r"fighting (for|against)",
        r"won the war",
        r"war (ration|time|era|years)",
        r"(world|civil|cold) war",
        r"battles? (with|against|for)",
        r"attack(ed|ing)? (the|a) problem",
        r"speed of light",
        r"explosion of",
        r"explod(e|ed|ing) (with|into)",
        r"fight back tears",
        r"fight for (justice|freedom|rights)",
        r"fighting? (cancer|disease|illness)",
        r"dead serious",
        r"pool table",
        r"bank shot",
        r"\ba beat\b",
        r"as if.*\b(molest|rape|seduce|fondle)",
        r"about to.*\b(molest|rape|seduce|fondle)",
        r"were to.*\b(molest|rape|seduce)",
        r"would.*\b(molest|rape|seduce)",
        r"brain(storm|wave|power|dump|drain|dead|cell|teaser|wash|freeze)",
        r"brain(s)? (are|is) (just|garbage|trash)",
        r"в курсе",
        r"курток",
        r"куртк\w",
        r"обритый наголо",
        r"наголо",
        r"таблетк\w+\s+(от|для|против)",
        r"болеутол\w+",
        r"кроват\w*",
        r"\bкров[ао](?:м|й|ю|е|й|и)?\b",
        r"мозгов(ой|ым|ого|ому|ая|ую)\s+(штурм|центр|атак|трест)",
        r"ран(ь|н)(ше|ий|яя|ее|его|им|ему)",
    ]

    CATEGORY_CONFIGS = {
        "profanity": {
            "patterns": PROFANITY_PATTERNS,
            "base_severity": 0.7,
            "rating_thresholds": {1: "6+", 3: "12+", 5: "16+", 10: "18+"},
        },
        "violence": {
            "patterns": VIOLENCE_PATTERNS,
            "base_severity": 0.6,
            "rating_thresholds": {1: "6+", 2: "12+", 4: "16+", 8: "18+"},
        },
        "gore": {
            "patterns": GORE_PATTERNS,
            "base_severity": 0.9,
            "rating_thresholds": {1: "16+", 2: "18+"},
        },
        "sex_act": {
            "patterns": SEX_PATTERNS,
            "base_severity": 0.8,
            "rating_thresholds": {1: "16+", 2: "18+"},
        },
        "nudity": {
            "patterns": NUDITY_PATTERNS,
            "base_severity": 0.6,
            "rating_thresholds": {1: "12+", 3: "16+", 5: "18+"},
        },
        "drugs": {
            "patterns": DRUG_PATTERNS,
            "base_severity": 0.7,
            "rating_thresholds": {1: "12+", 3: "16+", 5: "18+"},
        },
        "child_risk": {
            "patterns": CHILD_RISK_PATTERNS,
            "base_severity": 1.0,
            "rating_thresholds": {1: "18+"},
        },
    }

    @classmethod
    def analyze_script(
        cls, script_text: str, context_lines: int = 3
    ) -> Tuple[List[LineMatch], Dict[str, int]]:
        lines = script_text.split("\n")
        findings: List[LineMatch] = []
        category_counts: Dict[str, int] = {cat: 0 for cat in cls.CATEGORY_CONFIGS}

        for category, config in cls.CATEGORY_CONFIGS.items():
            matches = cls._find_category_matches(lines, category, config, context_lines)
            findings.extend(matches)
            category_counts[category] = len(matches)

        findings.sort(key=lambda x: (x.severity, x.line_start), reverse=True)
        return findings, category_counts

    @classmethod
    def _find_category_matches(
        cls,
        lines: List[str],
        category: str,
        config: Dict[str, Any],
        context_lines: int,
    ) -> List[LineMatch]:
        matches: List[LineMatch] = []
        patterns = config["patterns"]
        base_severity = config["base_severity"]
        false_positive_patterns = [
            re.compile(p, re.I | re.UNICODE) for p in cls.FALSE_POSITIVES
        ]

        for line_idx, line in enumerate(lines):
            line_lower = line.lower()
            total_matches = 0

            for pattern in patterns:
                matches_found = re.findall(
                    pattern, line_lower, flags=re.IGNORECASE | re.UNICODE
                )

                if matches_found:
                    context_start = max(0, line_idx - 10)
                    context_end = min(len(lines), line_idx + 11)
                    excerpt = " ".join(lines[context_start:context_end]).strip()

                    is_false_positive = any(
                        fp.search(excerpt) for fp in false_positive_patterns
                    )

                    if not is_false_positive:
                        total_matches += len(matches_found)

            if total_matches > 0:
                context_before = cls._get_context(lines, line_idx, context_lines, True)
                context_after = cls._get_context(lines, line_idx, context_lines, False)

                severity = min(base_severity * (1 + total_matches * 0.1), 1.0)
                rating_impact = cls._calculate_rating_impact(
                    total_matches, config["rating_thresholds"]
                )

                match = LineMatch(
                    line_start=line_idx + 1,
                    line_end=line_idx + 1,
                    category=category,
                    severity=severity,
                    matched_text=line.strip(),
                    context_before=context_before,
                    context_after=context_after,
                    match_count=total_matches,
                    rating_impact=rating_impact,
                )
                matches.append(match)

        return matches

    @classmethod
    def _get_context(
        cls, lines: List[str], line_idx: int, context_lines: int, before: bool
    ) -> List[str]:
        if before:
            start = max(0, line_idx - context_lines)
            end = line_idx
            return [lines[i].strip() for i in range(start, end) if i < len(lines)]
        else:
            start = line_idx + 1
            end = min(len(lines), line_idx + 1 + context_lines)
            return [lines[i].strip() for i in range(start, end) if i < len(lines)]

    @classmethod
    def _calculate_rating_impact(
        cls, match_count: int, thresholds: Dict[int, str]
    ) -> str:
        for count in sorted(thresholds.keys(), reverse=True):
            if match_count >= count:
                return thresholds[count]
        return "0+"

    @classmethod
    def get_summary_stats(cls, findings: List[LineMatch]) -> Dict[str, Any]:
        if not findings:
            return {
                "total_findings": 0,
                "by_category": {},
                "highest_severity": 0.0,
                "rating_impacts": {},
            }

        by_category = {}
        rating_impacts = {}

        for finding in findings:
            if finding.category not in by_category:
                by_category[finding.category] = {
                    "count": 0,
                    "total_matches": 0,
                    "avg_severity": 0.0,
                }

            by_category[finding.category]["count"] += 1
            by_category[finding.category]["total_matches"] += finding.match_count

            if finding.rating_impact not in rating_impacts:
                rating_impacts[finding.rating_impact] = 0
            rating_impacts[finding.rating_impact] += 1

        for category in by_category:
            count = by_category[category]["count"]
            by_category[category]["avg_severity"] = (
                sum(f.severity for f in findings if f.category == category) / count
            )

        return {
            "total_findings": len(findings),
            "by_category": by_category,
            "highest_severity": max(f.severity for f in findings),
            "rating_impacts": rating_impacts,
        }
