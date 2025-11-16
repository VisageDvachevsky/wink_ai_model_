from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from ..models.script import Script, ManualCorrection, LineFinding, Scene


class CorrectionService:
    @staticmethod
    async def add_false_positive(
        db: AsyncSession,
        script_id: int,
        finding_id: int = None,
        scene_id: int = None,
        description: str = None,
    ) -> ManualCorrection:
        correction = ManualCorrection(
            script_id=script_id,
            finding_id=finding_id,
            scene_id=scene_id,
            correction_type="false_positive",
            description=description,
            is_active=True,
        )
        db.add(correction)
        await db.commit()
        await db.refresh(correction)
        return correction

    @staticmethod
    async def add_false_negative(
        db: AsyncSession,
        script_id: int,
        category: str,
        severity: float,
        line_start: int = None,
        line_end: int = None,
        matched_text: str = None,
        description: str = None,
    ) -> ManualCorrection:
        correction = ManualCorrection(
            script_id=script_id,
            correction_type="false_negative",
            category=category,
            severity=severity,
            line_start=line_start,
            line_end=line_end,
            matched_text=matched_text,
            description=description,
            is_active=True,
        )
        db.add(correction)
        await db.commit()
        await db.refresh(correction)
        return correction

    @staticmethod
    async def get_corrections(
        db: AsyncSession, script_id: int
    ) -> tuple[List[ManualCorrection], Dict[str, int]]:
        result = await db.execute(
            select(ManualCorrection)
            .where(ManualCorrection.script_id == script_id)
            .where(ManualCorrection.is_active == True)
            .order_by(ManualCorrection.created_at.desc())
        )
        corrections = list(result.scalars().all())

        stats = {
            "false_positives": len(
                [c for c in corrections if c.correction_type == "false_positive"]
            ),
            "false_negatives": len(
                [c for c in corrections if c.correction_type == "false_negative"]
            ),
        }

        return corrections, stats

    @staticmethod
    async def delete_correction(db: AsyncSession, correction_id: int) -> bool:
        await db.execute(
            update(ManualCorrection)
            .where(ManualCorrection.id == correction_id)
            .values(is_active=False)
        )
        await db.commit()
        return True

    @staticmethod
    async def apply_corrections_to_rating(
        db: AsyncSession,
        script_id: int,
        base_rating: str,
        base_scores: Dict[str, float],
    ) -> tuple[str, Dict[str, float]]:
        corrections, stats = await CorrectionService.get_corrections(db, script_id)

        adjusted_scores = base_scores.copy()

        for correction in corrections:
            if correction.correction_type == "false_positive" and correction.category:
                if correction.category in adjusted_scores:
                    adjusted_scores[correction.category] = max(
                        0,
                        adjusted_scores[correction.category]
                        - (correction.severity or 0.1),
                    )
            elif correction.correction_type == "false_negative" and correction.category:
                if correction.category in adjusted_scores:
                    adjusted_scores[correction.category] = min(
                        1.0,
                        adjusted_scores[correction.category]
                        + (correction.severity or 0.2),
                    )

        adjusted_rating = CorrectionService._calculate_rating_from_scores(
            adjusted_scores
        )

        return adjusted_rating, adjusted_scores

    @staticmethod
    def _calculate_rating_from_scores(scores: Dict[str, float]) -> str:
        if scores.get("sex_act", 0) >= 0.75 or scores.get("gore", 0) >= 0.95:
            return "18+"
        elif scores.get("child_risk", 0) > 0.7 and (
            scores.get("sex_act", 0) >= 0.5 or scores.get("violence", 0) >= 0.8
        ):
            return "18+"
        elif (
            scores.get("violence", 0) >= 0.8 and scores.get("gore", 0) >= 0.7
        ) or scores.get("gore", 0) >= 0.75:
            return "16+"
        elif scores.get("violence", 0) >= 0.65 or scores.get("gore", 0) >= 0.5:
            return "16+"
        elif scores.get("sex_act", 0) >= 0.35 or scores.get("nudity", 0) >= 0.4:
            return "16+"
        elif (
            scores.get("violence", 0) >= 0.3
            or scores.get("profanity", 0) >= 0.4
            or scores.get("drugs", 0) >= 0.3
        ):
            return "12+"
        elif scores.get("violence", 0) >= 0.1 or scores.get("profanity", 0) >= 0.1:
            return "6+"
        else:
            return "0+"

    @staticmethod
    async def update_script_content(
        db: AsyncSession, script_id: int, new_content: str
    ) -> Script:
        result = await db.execute(select(Script).where(Script.id == script_id))
        script = result.scalar_one_or_none()

        if not script:
            raise ValueError(f"Script {script_id} not found")

        script.content = new_content
        await db.commit()
        await db.refresh(script)

        return script
