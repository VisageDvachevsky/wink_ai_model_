from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from ..models.script import Script, LineFinding, CharacterAnalysis
from .line_detector import LineDetector
from .character_analyzer import CharacterAnalyzer


class AnalysisService:
    @staticmethod
    async def analyze_and_save_line_findings(
        db: AsyncSession, script_id: int, script_text: str
    ) -> List[LineFinding]:
        await db.execute(delete(LineFinding).where(LineFinding.script_id == script_id))
        await db.commit()

        findings, category_counts = LineDetector.analyze_script(script_text)

        db_findings = []
        for finding in findings[:100]:
            db_finding = LineFinding(
                script_id=script_id,
                line_start=finding.line_start,
                line_end=finding.line_end,
                category=finding.category,
                severity=finding.severity,
                matched_text=finding.matched_text,
                context_before=(
                    "\n".join(finding.context_before)
                    if finding.context_before
                    else None
                ),
                context_after=(
                    "\n".join(finding.context_after) if finding.context_after else None
                ),
                match_count=finding.match_count,
                rating_impact=finding.rating_impact,
            )
            db.add(db_finding)
            db_findings.append(db_finding)

        await db.commit()

        for db_finding in db_findings:
            await db.refresh(db_finding)

        return db_findings

    @staticmethod
    async def get_line_findings(
        db: AsyncSession, script_id: int
    ) -> tuple[List[LineFinding], Dict[str, Any]]:
        result = await db.execute(
            select(LineFinding)
            .where(LineFinding.script_id == script_id)
            .order_by(LineFinding.severity.desc())
        )
        findings = list(result.scalars().all())

        by_category: Dict[str, Dict[str, Any]] = {}
        for finding in findings:
            if finding.category not in by_category:
                by_category[finding.category] = {
                    "count": 0,
                    "total_matches": 0,
                    "avg_severity": 0.0,
                }

            by_category[finding.category]["count"] += 1
            by_category[finding.category]["total_matches"] += finding.match_count

        for category in by_category:
            count = by_category[category]["count"]
            by_category[category]["avg_severity"] = (
                sum(f.severity for f in findings if f.category == category) / count
            )

        summary = {
            "total_findings": len(findings),
            "by_category": by_category,
        }

        return findings, summary

    @staticmethod
    async def analyze_and_save_characters(
        db: AsyncSession, script_id: int, script_text: str
    ) -> List[CharacterAnalysis]:
        await db.execute(
            delete(CharacterAnalysis).where(CharacterAnalysis.script_id == script_id)
        )
        await db.commit()

        character_stats = CharacterAnalyzer.analyze_characters(script_text)

        db_characters = []
        for stats in character_stats[:50]:
            db_character = CharacterAnalysis(
                script_id=script_id,
                character_name=stats.name,
                profanity_count=stats.profanity_count,
                violence_scenes=stats.violence_scenes,
                sex_scenes=stats.sex_scenes,
                drug_scenes=stats.drug_scenes,
                total_problematic_scenes=stats.total_problematic_scenes,
                severity_score=stats.severity_score,
                recommendations={"items": stats.recommendations},
                scene_appearances=stats.scene_appearances,
            )
            db.add(db_character)
            db_characters.append(db_character)

        await db.commit()

        for db_character in db_characters:
            await db.refresh(db_character)

        return db_characters

    @staticmethod
    async def get_character_analysis(
        db: AsyncSession, script_id: int
    ) -> List[CharacterAnalysis]:
        result = await db.execute(
            select(CharacterAnalysis)
            .where(CharacterAnalysis.script_id == script_id)
            .order_by(CharacterAnalysis.severity_score.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def run_full_analysis(db: AsyncSession, script_id: int) -> Dict[str, Any]:
        result = await db.execute(select(Script).where(Script.id == script_id))
        script = result.scalar_one_or_none()

        if not script:
            raise ValueError(f"Script {script_id} not found")

        script_text = str(script.content)

        line_findings = await AnalysisService.analyze_and_save_line_findings(
            db, script_id, script_text
        )

        character_analyses = await AnalysisService.analyze_and_save_characters(
            db, script_id, script_text
        )

        return {
            "line_findings_count": len(line_findings),
            "character_count": len(character_analyses),
        }
