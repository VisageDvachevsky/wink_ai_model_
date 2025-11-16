from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.base import get_db
from ...services.detection_service import DetectionService
from ...services.ml_client import ml_client
from ...schemas.detection import (
    LineDetectionResponse,
    UserCorrectionCreate,
    UserCorrectionResponse,
    LineDetectionStatsResponse,
    ScriptWithDetectionsResponse,
)

router = APIRouter()


@router.post("/{script_id}/detections", response_model=List[LineDetectionResponse])
async def detect_lines(
    script_id: int,
    context_size: int = 3,
    db: AsyncSession = Depends(get_db),
):
    """Detect problematic lines in script."""
    service = DetectionService(db, ml_client)
    try:
        detections = await service.detect_and_store_lines(script_id, context_size)
        return detections
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect lines: {str(e)}",
        )


@router.get("/{script_id}/detections", response_model=List[LineDetectionResponse])
async def get_detections(
    script_id: int,
    include_false_positives: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """Get all detections for a script."""
    service = DetectionService(db, ml_client)
    try:
        detections = await service.get_detections(script_id, include_false_positives)
        return detections
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get detections: {str(e)}",
        )


@router.get("/{script_id}/detections/stats", response_model=LineDetectionStatsResponse)
async def get_detection_stats(
    script_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get detection statistics for a script."""
    service = DetectionService(db, ml_client)
    try:
        stats = await service.get_detection_stats(script_id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}",
        )


@router.patch("/detections/{detection_id}/false-positive")
async def mark_false_positive(
    detection_id: int,
    is_false_positive: bool,
    db: AsyncSession = Depends(get_db),
):
    """Mark a detection as false positive."""
    service = DetectionService(db, ml_client)
    try:
        detection = await service.mark_false_positive(detection_id, is_false_positive)
        return detection
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update detection: {str(e)}",
        )


@router.post("/{script_id}/corrections", response_model=UserCorrectionResponse)
async def create_correction(
    script_id: int,
    correction: UserCorrectionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a user correction."""
    service = DetectionService(db, ml_client)
    try:
        result = await service.create_correction(correction)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create correction: {str(e)}",
        )


@router.get("/{script_id}/corrections", response_model=List[UserCorrectionResponse])
async def get_corrections(
    script_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all corrections for a script."""
    service = DetectionService(db, ml_client)
    try:
        corrections = await service.get_corrections(script_id)
        return corrections
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get corrections: {str(e)}",
        )


@router.get("/{script_id}/detections/full", response_model=ScriptWithDetectionsResponse)
async def get_script_with_detections(
    script_id: int,
    include_false_positives: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """Get script with all detections and stats."""
    from sqlalchemy import select
    from ...models.script import Script

    service = DetectionService(db, ml_client)

    try:
        result = await db.execute(select(Script).where(Script.id == script_id))
        script = result.scalar_one_or_none()

        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Script {script_id} not found",
            )

        detections = await service.get_detections(script_id, include_false_positives)
        stats = await service.get_detection_stats(script_id)
        corrections = await service.get_corrections(script_id)

        return ScriptWithDetectionsResponse(
            script_id=script_id,
            title=script.title,
            predicted_rating=script.predicted_rating,
            detections=detections,
            stats=stats,
            correction_count=len(corrections),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get script with detections: {str(e)}",
        )
