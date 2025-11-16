from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...db.base import get_db
from ...models.script import Script, ManualCorrection
from ...services.ml_client import ml_client
from ...core.exceptions import ScriptNotFoundError

router = APIRouter(prefix="/scripts", tags=["line-detection"])


@router.get("/{script_id}/detect-lines")
async def detect_lines_in_script(
    script_id: int,
    context_lines: int = 3,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Script).where(Script.id == script_id))
    script = result.scalar_one_or_none()

    if not script:
        raise ScriptNotFoundError(script_id)

    detection_result = await ml_client.detect_lines(
        text=str(script.content), context_lines=context_lines
    )

    stmt = select(ManualCorrection).where(ManualCorrection.script_id == script_id)
    corrections_result = await db.execute(stmt)
    corrections = corrections_result.scalars().all()

    corrections_map = {}
    for corr in corrections:
        key = f"{corr.category}_{corr.line_number}"
        corrections_map[key] = {
            "type": corr.correction_type,
            "notes": corr.notes,
            "created_at": corr.created_at.isoformat() if corr.created_at else None,
        }

    for issue in detection_result.get("issues", []):
        key = f"{issue['category']}_{issue['line_number']}"
        if key in corrections_map:
            issue["correction"] = corrections_map[key]

    return detection_result


@router.post("/{script_id}/corrections")
async def save_corrections(
    script_id: int,
    corrections: list[dict],
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Script).where(Script.id == script_id))
    script = result.scalar_one_or_none()

    if not script:
        raise ScriptNotFoundError(script_id)

    for corr_data in corrections:
        correction = ManualCorrection(
            script_id=script_id,
            issue_id=corr_data["issue_id"],
            correction_type=corr_data["correction_type"],
            category=corr_data["category"],
            line_number=corr_data["line_number"],
            notes=corr_data.get("notes"),
        )
        db.add(correction)

    await db.commit()

    return {"status": "success", "corrections_saved": len(corrections)}


@router.get("/{script_id}/corrections")
async def get_corrections(
    script_id: int,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(ManualCorrection).where(ManualCorrection.script_id == script_id)
    result = await db.execute(stmt)
    corrections = result.scalars().all()

    return {
        "script_id": script_id,
        "corrections": [
            {
                "id": corr.id,
                "issue_id": corr.issue_id,
                "correction_type": corr.correction_type,
                "category": corr.category,
                "line_number": corr.line_number,
                "notes": corr.notes,
                "created_at": corr.created_at.isoformat() if corr.created_at else None,
            }
            for corr in corrections
        ],
    }


@router.delete("/{script_id}/corrections/{correction_id}")
async def delete_correction(
    script_id: int,
    correction_id: int,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(ManualCorrection).where(
        ManualCorrection.id == correction_id, ManualCorrection.script_id == script_id
    )
    result = await db.execute(stmt)
    correction = result.scalar_one_or_none()

    if not correction:
        raise HTTPException(status_code=404, detail="Correction not found")

    await db.delete(correction)
    await db.commit()

    return {"status": "success", "deleted_id": correction_id}
