"""
Line-level detection module for identifying specific problematic lines in scripts.
Provides detailed line-by-line analysis with context.
"""

import re
from typing import List, Dict, Any
from loguru import logger


CATEGORY_PATTERNS = {
    "violence": [
        r"\bkill\w*", r"\bshoot\w*", r"\bshot\b", r"\bstab\w*", r"\bknife\b",
        r"\bgun\w*", r"\bpistol\b", r"\brifle\b", r"\bexplod\w*", r"\bblast\w*",
        r"\battack\w*", r"\bbeating\b", r"\bbeaten\b", r"\bbeats\b", r"\bcorpse\b",
        r"\bdead\b", r"\bmurder\w*", r"\bviolence\b", r"\bterrorist\b", r"\bhostage\b",
        r"\brip(ped|s)? apart\b", r"\bthug(s)?\b", r"\bterror\b",
        r"\bfight(ing)?\b", r"\bbattle(s|d)?\b", r"\bwar\b", r"\bshoot[- ]?out\b",
        r"\bexplosion\b", r"\bgrenade\b",
        r"\bубий\w*", r"\bубить\b", r"\bубил\w*", r"\bубива\w*",
        r"\bстреля\w*", r"\bвыстрел\w*", r"\bзастрел\w*", r"\bзарез\w*",
        r"\bнож\b", r"\bоруж\w+", r"\bпистолет\w*", r"\bвинтовк\w*",
        r"\bавтомат\w*", r"\bвзрыв\w*", r"\bатак\w*", r"\bнападе\w*",
        r"\bизбие\w*", r"\bтруп\w*", r"\bмертв\w*", r"\bпогиб\w*",
        r"\bнасилие\b", r"\bжесток\w*", r"\bтеррор\w*", r"\bзаложник\w*",
        r"\bбандит\w*", r"\bдрак\w*", r"\bбой\b", r"\bсраж\w*",
        r"\bвойна\b", r"\bбоев\w*", r"\bгранат\w*", r"\bбомб\w*",
    ],
    "gore": [
        r"\bblood\b", r"\bbloody\b", r"\bbloodied\b", r"\bbleeding\b",
        r"\bcorpse\b", r"\bwound\b", r"\bscar\b", r"\binjur\w*",
        r"\bcrash\w*", r"\bburn\w*", r"\bguts\b", r"\bentrails\b",
        r"\bbrain\b", r"\bdead body\b", r"\bgore\b", r"\bmutilat\w*",
        r"\bкровь\b", r"\bкров[ьи]ю\b", r"\bкровав\w*", r"\bкровоточ\w*",
        r"\bран(?:а|ы|у|ой|е|ам|ами|ах)\b", r"\bшрам\w*", r"\bувечь\w*",
        r"\bожог\w*", r"\bкишк\w*", r"\bвнутренност\w*",
        r"\bмозг(?:и|ов|у|ом|ах|ами)?\b", r"\bрасчленен\w*", r"\bизувеч\w*",
    ],
    "profanity": [
        r"\bfuck\b", r"\bshit\b", r"\bmotherfucker\b", r"\bbitch\b",
        r"\basshole\b", r"\bdamn\b", r"\bhell\b", r"\bcrap\b",
        r"\bблядь\b", r"\bбля\b", r"\bсука\b", r"\bхуй\b",
        r"\bпизд\w*", r"\bебать\b", r"\bебал\w*", r"\bебан\w*",
        r"\bзаеб\w*", r"\bдерьм\w*", r"\bговн\w*", r"\bхер\w*",
        r"\bмудак\w*", r"\bсволоч\w*", r"\bтварь\b",
    ],
    "drugs": [
        r"\bdrug(s)?\b", r"\bheroin\b", r"\bcocaine\b", r"\bmarijuana\b",
        r"\bpill(s)?\b", r"\bweed\b", r"\balcohol\b", r"\bdrunk\b",
        r"\bcigarette\b", r"\bsmok(e|ing)\b", r"\baddiction\b",
        r"\bнаркот\w*", r"\bгероин\w*", r"\bкокаин\w*", r"\bмарихуан\w*",
        r"\bтравк\w*", r"\bдоп\w*", r"\bтаблетк\w*", r"\bпилюл\w*",
        r"\bалкогол\w*", r"\bспирт\w*", r"\bвыпив\w*", r"\bпьян\w*",
        r"\bсигарет\w*", r"\bкур\w*", r"\bзависим\w*", r"\bнакур\w*",
    ],
    "sex_act": [
        r"\brape\b", r"\bsexual\b", r"\bintercourse\b", r"\bsex scene\b",
        r"\bmolest\b", r"\borgasm\b", r"\bmake love\b", r"\bhaving sex\b",
        r"\bsexually\b", r"\bbed\s+scene\b",
        r"\bизнасилов\w*", r"\bнасилов\w*", r"\bсексуальн\w*",
        r"\bполов\w+\s+акт\w*", r"\bинтимн\w*", r"\bоргазм\w*",
        r"\bзанимаются\s+сексом\b",
    ],
    "nudity": [
        r"\bbra\b", r"\bpanty|panties\b", r"\bunderwear\b",
        r"\bnaked\b", r"\bnude\b", r"\bundress\w*", r"\btopless\b",
        r"\bголый\b", r"\bголая\b", r"\bнаг\w*", r"\bобнаж\w*",
        r"\bбюстгальтер\w*", r"\bтрус\w*", r"\bбелье\b",
        r"\bраздева\w*", r"\bбез одежд\w*",
    ],
    "child_risk": [
        r"\bchild(ren)?\b.*\b(danger|threat|harm|abuse|violence)\b",
        r"\bkid(s)?\b.*\b(danger|threat|harm|abuse|violence)\b",
        r"\bchild abuse\b", r"\bchild endangerment\b", r"\bpedophil\w*",
        r"\bминор\w*", r"\bнесовершеннолетн\w*",
        r"\bребенок\b.*\b(опасност|угроз|насили|избие)\w*",
        r"\bдет\w+.*\b(опасност|угроз|насили|избие)\w*",
        r"\bжестокое обращение с детьми\b",
    ],
}


class LineDetector:
    def __init__(self):
        self.compiled_patterns = {}
        for category, patterns in CATEGORY_PATTERNS.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
        logger.info(f"LineDetector initialized with {len(CATEGORY_PATTERNS)} categories")

    def detect_lines(
        self, text: str, context_size: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Detect problematic lines in script with context.

        Args:
            text: Script content
            context_size: Number of lines before/after to include as context

        Returns:
            List of detections with line numbers, text, context, category, and matches
        """
        lines = text.split('\n')
        detections = []

        for line_idx, line in enumerate(lines):
            line_num = line_idx + 1

            for category, patterns in self.compiled_patterns.items():
                matches = []
                matched_texts = set()

                for pattern in patterns:
                    for match in pattern.finditer(line):
                        matched_text = match.group(0)
                        if matched_text.lower() not in matched_texts:
                            matched_texts.add(matched_text.lower())
                            matches.append({
                                "text": matched_text,
                                "start": match.start(),
                                "end": match.end(),
                                "pattern": pattern.pattern
                            })

                if matches:
                    context_before = self._get_context_lines(
                        lines, line_idx, -context_size, 0
                    )
                    context_after = self._get_context_lines(
                        lines, line_idx, 1, context_size + 1
                    )

                    severity = self._calculate_severity(category, len(matches), line)

                    detections.append({
                        "line_start": line_num,
                        "line_end": line_num,
                        "detected_text": line.strip(),
                        "context_before": '\n'.join(context_before) if context_before else None,
                        "context_after": '\n'.join(context_after) if context_after else None,
                        "category": category,
                        "severity": severity,
                        "matched_patterns": {
                            "count": len(matches),
                            "matches": matches
                        }
                    })

        logger.info(f"Detected {len(detections)} problematic lines in script")
        return detections

    def get_statistics(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics from detections."""
        stats = {
            "total_detections": len(detections),
            "by_category": {},
            "total_matches": {},
        }

        for detection in detections:
            category = detection["category"]
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1

            match_count = detection.get("matched_patterns", {}).get("count", 0)
            stats["total_matches"][category] = (
                stats["total_matches"].get(category, 0) + match_count
            )

        return stats

    def _get_context_lines(
        self, lines: List[str], current_idx: int, start_offset: int, end_offset: int
    ) -> List[str]:
        """Extract context lines around a specific line."""
        start = max(0, current_idx + start_offset)
        end = min(len(lines), current_idx + end_offset)
        context = []

        for i in range(start, end):
            if i != current_idx:
                context.append(lines[i].strip())

        return context

    def _calculate_severity(self, category: str, match_count: int, line: str) -> float:
        """Calculate severity score based on category and matches."""
        base_severity = {
            "profanity": 0.3,
            "violence": 0.5,
            "gore": 0.6,
            "drugs": 0.4,
            "sex_act": 0.7,
            "nudity": 0.5,
            "child_risk": 0.9,
        }

        severity = base_severity.get(category, 0.5)

        severity += min(match_count * 0.1, 0.3)

        if any(word in line.lower() for word in ["graphic", "explicit", "extreme", "brutal"]):
            severity += 0.2

        return min(severity, 1.0)
