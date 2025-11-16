import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from .repair_pipeline import (
    VIOLENCE_WORDS,
    GORE_WORDS,
    PROFANITY,
    DRUG_WORDS,
    SEX_WORDS,
    NUDITY_WORDS,
    CHILD_WORDS,
)


@dataclass
class LineIssue:
    line_number: int
    line_text: str
    category: str
    matched_words: List[str]
    context_before: List[Tuple[int, str]]
    context_after: List[Tuple[int, str]]
    severity: float


class LineDetector:
    def __init__(self):
        self.patterns = {
            "profanity": PROFANITY,
            "violence": VIOLENCE_WORDS,
            "gore": GORE_WORDS,
            "drugs": DRUG_WORDS,
            "sex_act": SEX_WORDS,
            "nudity": NUDITY_WORDS,
            "child_risk": CHILD_WORDS,
        }

    def detect_issues_in_text(
        self, text: str, context_lines: int = 3
    ) -> Dict[str, Any]:
        lines = text.split("\n")
        all_issues: List[LineIssue] = []
        category_stats = {cat: 0 for cat in self.patterns.keys()}

        for line_num, line in enumerate(lines, start=1):
            line_lower = line.lower()

            for category, patterns in self.patterns.items():
                matched_words = []

                for pattern in patterns:
                    if isinstance(pattern, re.Pattern):
                        regex = pattern
                    else:
                        regex = re.compile(pattern, re.I)

                    matches = list(regex.finditer(line_lower))
                    if matches:
                        for match in matches:
                            matched_words.append(line[match.start() : match.end()])

                if matched_words:
                    context_before = self._get_context_lines(
                        lines, line_num, -context_lines, 0
                    )
                    context_after = self._get_context_lines(
                        lines, line_num, 1, context_lines + 1
                    )

                    severity = self._calculate_severity(category, len(matched_words))

                    issue = LineIssue(
                        line_number=line_num,
                        line_text=line.strip(),
                        category=category,
                        matched_words=matched_words,
                        context_before=context_before,
                        context_after=context_after,
                        severity=severity,
                    )
                    all_issues.append(issue)
                    category_stats[category] += len(matched_words)

        sorted_issues = sorted(
            all_issues, key=lambda x: (x.severity, x.line_number), reverse=True
        )

        return {
            "total_issues": len(sorted_issues),
            "issues": [self._issue_to_dict(issue) for issue in sorted_issues],
            "statistics": category_stats,
            "summary": self._generate_summary(category_stats, len(lines)),
        }

    def _get_context_lines(
        self, lines: List[str], current_line: int, start_offset: int, end_offset: int
    ) -> List[Tuple[int, str]]:
        result = []
        for offset in range(start_offset, end_offset):
            idx = current_line - 1 + offset
            if 0 <= idx < len(lines):
                result.append((idx + 1, lines[idx].strip()))
        return result

    def _calculate_severity(self, category: str, count: int) -> float:
        base_severity = {
            "profanity": 0.5,
            "violence": 0.7,
            "gore": 0.8,
            "drugs": 0.6,
            "sex_act": 0.9,
            "nudity": 0.6,
            "child_risk": 0.95,
        }
        return base_severity.get(category, 0.5) * min(count / 3.0 + 0.5, 2.0)

    def _issue_to_dict(self, issue: LineIssue) -> Dict[str, Any]:
        return {
            "line_number": issue.line_number,
            "line_text": issue.line_text,
            "category": issue.category,
            "matched_words": issue.matched_words,
            "match_count": len(issue.matched_words),
            "context_before": [
                {"line": ln, "text": txt} for ln, txt in issue.context_before
            ],
            "context_after": [
                {"line": ln, "text": txt} for ln, txt in issue.context_after
            ],
            "severity": round(issue.severity, 2),
        }

    def _generate_summary(
        self, stats: Dict[str, int], total_lines: int
    ) -> Dict[str, Any]:
        total_matches = sum(stats.values())
        return {
            "total_lines": total_lines,
            "total_matches": total_matches,
            "density": round(total_matches / max(total_lines, 1), 4),
            "category_breakdown": stats,
            "most_common_category": max(stats, key=stats.get) if stats else None,
        }


def detect_lines(text: str, context_lines: int = 3) -> Dict[str, Any]:
    detector = LineDetector()
    return detector.detect_issues_in_text(text, context_lines)
