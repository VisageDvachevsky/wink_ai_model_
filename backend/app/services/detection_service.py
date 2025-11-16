from typing import List, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.script import Script, LineDetection, UserCorrection
from ..schemas.detection import (
    LineDetectionResponse,
    UserCorrectionCreate,
    UserCorrectionResponse,
    LineDetectionStatsResponse,
    CategoryGradation,
)
from .ml_client import MLClient
from ..utils.parents_guide import (
    severity_to_gradation,
    get_category_description,
    CATEGORY_LABELS,
)


class DetectionService:
    def __init__(self, db: AsyncSession, ml_client: MLClient):
        self.db = db
        self.ml_client = ml_client

    async def detect_and_store_lines(
        self, script_id: int, context_size: int = 3
    ) -> List[LineDetectionResponse]:
        """Detect problematic lines in script and store them."""
        result = await self.db.execute(select(Script).where(Script.id == script_id))
        script = result.scalar_one_or_none()

        if not script:
            raise ValueError(f"Script {script_id} not found")

        await self.db.execute(
            select(LineDetection).where(LineDetection.script_id == script_id)
        )
        existing = await self.db.execute(
            select(LineDetection).where(LineDetection.script_id == script_id)
        )
        for detection in existing.scalars():
            await self.db.delete(detection)

        ml_result = await self.ml_client.detect_lines(
            script.content, str(script_id), context_size
        )

        detections = []
        for item in ml_result.get("detections", []):
            detection = LineDetection(
                script_id=script_id,
                line_start=item["line_start"],
                line_end=item["line_end"],
                detected_text=item["detected_text"],
                context_before=item.get("context_before"),
                context_after=item.get("context_after"),
                category=item["category"],
                severity=item["severity"],
                matched_patterns=item.get("matched_patterns"),
                page_number=item.get("page_number"),
                character=item.get("character"),
                scene_number=item.get("scene_number"),
                scene_heading=item.get("scene_heading"),
                timing_estimate=item.get("timing_estimate"),
            )
            self.db.add(detection)
            detections.append(detection)

        await self.db.commit()

        return [
            LineDetectionResponse.model_validate(d) for d in detections
        ]

    async def get_detections(
        self, script_id: int, include_false_positives: bool = False
    ) -> List[LineDetectionResponse]:
        """Get all detections for a script."""
        query = select(LineDetection).where(LineDetection.script_id == script_id)

        if not include_false_positives:
            query = query.where(LineDetection.is_false_positive.is_(False))

        result = await self.db.execute(query)
        detections = result.scalars().all()

        return [LineDetectionResponse.model_validate(d) for d in detections]

    async def get_detection_stats(
        self, script_id: int
    ) -> LineDetectionStatsResponse:
        """Get statistics for script detections."""
        result = await self.db.execute(
            select(LineDetection).where(LineDetection.script_id == script_id)
        )
        detections = result.scalars().all()

        script_result = await self.db.execute(
            select(Script).where(Script.id == script_id)
        )
        script = script_result.scalar_one_or_none()
        total_scenes = script.total_scenes if script and script.total_scenes else 0

        stats = LineDetectionStatsResponse(
            total_detections=len(detections),
            by_category={},
            total_matches={},
            false_positives=sum(1 for d in detections if d.is_false_positive),
            user_corrections=sum(1 for d in detections if d.user_corrected),
        )

        category_data: Dict[str, Dict] = {}
        for detection in detections:
            if detection.is_false_positive:
                continue

            category = detection.category
            stats.by_category[category] = stats.by_category.get(category, 0) + 1

            match_count = detection.matched_patterns.get("count", 0) if detection.matched_patterns else 0
            stats.total_matches[category] = stats.total_matches.get(category, 0) + match_count

            if category not in category_data:
                category_data[category] = {
                    "episodes": 0,
                    "max_severity": 0.0,
                    "scenes": set(),
                }

            category_data[category]["episodes"] += 1
            category_data[category]["max_severity"] = max(
                category_data[category]["max_severity"], detection.severity
            )
            if detection.scene_id:
                category_data[category]["scenes"].add(detection.scene_id)

        parents_guide = []
        for category, data in category_data.items():
            severity_score = data["max_severity"]
            gradation = severity_to_gradation(severity_score)
            affected_scenes = len(data["scenes"])
            percentage = (affected_scenes / total_scenes * 100) if total_scenes > 0 else 0

            label = CATEGORY_LABELS.get(category, category.replace("_", " ").title())

            parents_guide.append(
                CategoryGradation(
                    category=label,
                    gradation=gradation,
                    episodes=data["episodes"],
                    affected_scenes_count=affected_scenes,
                    total_scenes=total_scenes,
                    percentage=round(percentage, 1),
                    severity_score=round(severity_score, 2),
                    description=get_category_description(
                        category, data["episodes"], gradation
                    ),
                )
            )

        parents_guide.sort(key=lambda x: x.severity_score, reverse=True)
        stats.parents_guide = parents_guide

        return stats

    async def mark_false_positive(
        self, detection_id: int, is_false_positive: bool
    ) -> LineDetectionResponse:
        """Mark detection as false positive."""
        result = await self.db.execute(
            select(LineDetection).where(LineDetection.id == detection_id)
        )
        detection = result.scalar_one_or_none()

        if not detection:
            raise ValueError(f"Detection {detection_id} not found")

        detection.is_false_positive = is_false_positive
        detection.user_corrected = True
        await self.db.commit()
        await self.db.refresh(detection)

        return LineDetectionResponse.model_validate(detection)

    async def create_correction(
        self, correction_data: UserCorrectionCreate
    ) -> UserCorrectionResponse:
        """Create a user correction."""
        correction = UserCorrection(**correction_data.model_dump())
        self.db.add(correction)
        await self.db.commit()
        await self.db.refresh(correction)

        return UserCorrectionResponse.model_validate(correction)

    async def get_corrections(
        self, script_id: int
    ) -> List[UserCorrectionResponse]:
        """Get all corrections for a script."""
        result = await self.db.execute(
            select(UserCorrection).where(UserCorrection.script_id == script_id)
        )
        corrections = result.scalars().all()

        return [UserCorrectionResponse.model_validate(c) for c in corrections]
