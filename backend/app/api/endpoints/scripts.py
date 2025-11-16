import asyncio
from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from ...db.base import get_db
from ...schemas.script import (
    ScriptCreate,
    ScriptResponse,
    ScriptDetailResponse,
    RatingJobResponse,
    WhatIfRequest,
    WhatIfResponse,
    LineFindingsSummaryResponse,
    LineFindingResponse,
    CharacterAnalysisSummaryResponse,
    CharacterAnalysisResponse,
    ManualCorrectionCreate,
    ManualCorrectionResponse,
    CorrectionsSummaryResponse,
    ScriptUpdateRequest,
    AdjustedRatingResponse,
    AISuggestRequest,
)
from ...services.script_service import script_service
from ...services.ml_client import ml_client
from ...services.queue import enqueue_rating_job, get_job_status
from ...services.pdf_generator import PDFReportGenerator
from ...services.export_service import ExportService
from ...services.document_parser import DocumentParser
from ...services.analysis_service import AnalysisService
from ...services.correction_service import CorrectionService
from ...core.exceptions import (
    ScriptNotFoundError,
    InvalidFileError,
    FileTooLargeError,
)
from ...core.config import settings

router = APIRouter(prefix="/scripts", tags=["scripts"])


@router.post("/", response_model=ScriptResponse, status_code=201)
async def create_script(script: ScriptCreate, db: AsyncSession = Depends(get_db)):
    new_script = await script_service.create_script(db, script)
    return new_script


@router.post("/upload", response_model=ScriptResponse, status_code=201)
async def upload_script(
    file: UploadFile = File(...),
    title: str = Form(None),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename:
        raise InvalidFileError("Filename is required")

    file_extension = "." + file.filename.split(".")[-1].lower()
    if file_extension not in settings.allowed_file_extensions:
        raise InvalidFileError(
            f"File type {file_extension} not allowed. Allowed types: {', '.join(settings.allowed_file_extensions)}"
        )

    content = await file.read()

    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_size_bytes:
        raise FileTooLargeError(settings.max_upload_size_mb)

    text = DocumentParser.parse_document(content, file.filename)

    if not text or not text.strip():
        raise InvalidFileError(
            f"Could not extract text from {file_extension} file. "
            "Please ensure the file contains readable text."
        )

    script_title = title or file.filename or "Untitled Script"
    script_data = ScriptCreate(title=script_title, content=text)

    new_script = await script_service.create_script(db, script_data)
    return new_script


@router.get("/", response_model=list[ScriptResponse])
async def list_scripts(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    scripts = await script_service.list_scripts(db, skip, limit)
    return scripts


@router.get("/{script_id}", response_model=ScriptDetailResponse)
async def get_script(script_id: int, db: AsyncSession = Depends(get_db)):
    script = await script_service.get_script(db, script_id)
    if not script:
        raise ScriptNotFoundError(script_id)
    return script


@router.post("/{script_id}/rate", response_model=RatingJobResponse)
async def rate_script(
    script_id: int, background: bool = True, db: AsyncSession = Depends(get_db)
):
    script = await script_service.get_script(db, script_id)
    if not script:
        raise ScriptNotFoundError(script_id)

    if background:
        job_id = await enqueue_rating_job(script_id)
        return RatingJobResponse(
            job_id=job_id,
            script_id=script_id,
            status="queued",
            message="Rating job has been queued",
        )
    else:
        await script_service.process_rating(db, script_id)
        return RatingJobResponse(
            job_id="sync",
            script_id=script_id,
            status="completed",
            message="Rating completed synchronously",
        )


@router.get("/jobs/{job_id}/status")
async def get_rating_job_status(job_id: str):
    status = await get_job_status(job_id)
    return status


@router.post("/{script_id}/what-if", response_model=WhatIfResponse)
async def what_if_analysis(
    script_id: int, request: WhatIfRequest, db: AsyncSession = Depends(get_db)
):
    script = await script_service.get_script(db, script_id)
    if not script:
        raise ScriptNotFoundError(script_id)

    result = await ml_client.what_if_analysis(
        script_text=str(script.content),
        modification_request=request.modification_request,
    )

    return WhatIfResponse(**result)


@router.get("/{script_id}/export/pdf")
async def export_pdf(script_id: int, db: AsyncSession = Depends(get_db)):
    script = await script_service.get_script(db, script_id)
    if not script:
        raise ScriptNotFoundError(script_id)

    generator = PDFReportGenerator(language="ru")
    pdf_buffer = generator.generate_report(script=script, scenes=script.scenes or [])

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=rating_report_{script_id}.pdf"
        },
    )


@router.get("/{script_id}/export/excel")
async def export_excel(script_id: int, db: AsyncSession = Depends(get_db)):
    script = await script_service.get_script(db, script_id)
    if not script:
        raise ScriptNotFoundError(script_id)

    excel_buffer = ExportService.export_to_excel(
        script=script, scenes=script.scenes or []
    )

    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=rating_report_{script_id}.xlsx"
        },
    )


@router.get("/{script_id}/export/csv")
async def export_csv(script_id: int, db: AsyncSession = Depends(get_db)):
    script = await script_service.get_script(db, script_id)
    if not script:
        raise ScriptNotFoundError(script_id)

    csv_output = ExportService.export_to_csv(script=script, scenes=script.scenes or [])

    return StreamingResponse(
        csv_output,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=rating_report_{script_id}.csv"
        },
    )


@router.get("/{script_id}/line-findings", response_model=LineFindingsSummaryResponse)
async def get_line_findings(script_id: int, db: AsyncSession = Depends(get_db)):
    script = await script_service.get_script(db, script_id)
    if not script:
        raise ScriptNotFoundError(script_id)

    findings, summary = await AnalysisService.get_line_findings(db, script_id)

    return LineFindingsSummaryResponse(
        total_findings=summary["total_findings"],
        by_category=summary["by_category"],
        findings=[LineFindingResponse.from_orm(f) for f in findings],
    )


@router.get(
    "/{script_id}/character-analysis", response_model=CharacterAnalysisSummaryResponse
)
async def get_character_analysis(script_id: int, db: AsyncSession = Depends(get_db)):
    script = await script_service.get_script(db, script_id)
    if not script:
        raise ScriptNotFoundError(script_id)

    characters = await AnalysisService.get_character_analysis(db, script_id)

    top_offenders = sorted(characters, key=lambda x: x.severity_score, reverse=True)[:5]

    return CharacterAnalysisSummaryResponse(
        total_characters=len(characters),
        top_offenders=[CharacterAnalysisResponse.from_orm(c) for c in top_offenders],
        all_characters=[CharacterAnalysisResponse.from_orm(c) for c in characters],
    )


@router.post("/{script_id}/analyze", status_code=202)
async def trigger_analysis(script_id: int, db: AsyncSession = Depends(get_db)):
    script = await script_service.get_script(db, script_id)
    if not script:
        raise ScriptNotFoundError(script_id)

    result = await AnalysisService.run_full_analysis(db, script_id)

    return {
        "script_id": script_id,
        "status": "completed",
        "line_findings_count": result["line_findings_count"],
        "character_count": result["character_count"],
    }


@router.post(
    "/{script_id}/corrections", response_model=ManualCorrectionResponse, status_code=201
)
async def create_correction(
    script_id: int,
    correction: ManualCorrectionCreate,
    db: AsyncSession = Depends(get_db),
):
    script = await script_service.get_script(db, script_id)
    if not script:
        raise ScriptNotFoundError(script_id)

    if correction.correction_type == "false_positive":
        result = await CorrectionService.add_false_positive(
            db,
            script_id,
            finding_id=correction.finding_id,
            scene_id=correction.scene_id,
            description=correction.description,
        )
    else:
        result = await CorrectionService.add_false_negative(
            db,
            script_id,
            category=correction.category or "unknown",
            severity=correction.severity or 0.5,
            line_start=correction.line_start,
            line_end=correction.line_end,
            matched_text=correction.matched_text,
            description=correction.description,
        )

    return ManualCorrectionResponse.from_orm(result)


@router.get("/{script_id}/corrections", response_model=CorrectionsSummaryResponse)
async def get_corrections(script_id: int, db: AsyncSession = Depends(get_db)):
    script = await script_service.get_script(db, script_id)
    if not script:
        raise ScriptNotFoundError(script_id)

    corrections, stats = await CorrectionService.get_corrections(db, script_id)

    return CorrectionsSummaryResponse(
        corrections=[ManualCorrectionResponse.from_orm(c) for c in corrections],
        stats=stats,
    )


@router.delete("/{script_id}/corrections/{correction_id}", status_code=204)
async def delete_correction(
    script_id: int, correction_id: int, db: AsyncSession = Depends(get_db)
):
    await CorrectionService.delete_correction(db, correction_id)
    return {"status": "deleted"}


@router.get("/{script_id}/adjusted-rating", response_model=AdjustedRatingResponse)
async def get_adjusted_rating(script_id: int, db: AsyncSession = Depends(get_db)):
    script = await script_service.get_script(db, script_id)
    if not script:
        raise ScriptNotFoundError(script_id)

    if not script.predicted_rating or not script.agg_scores:
        return AdjustedRatingResponse(
            original_rating="0+",
            adjusted_rating="0+",
            original_scores={},
            adjusted_scores={},
            corrections_applied=0,
        )

    adjusted_rating, adjusted_scores = (
        await CorrectionService.apply_corrections_to_rating(
            db, script_id, script.predicted_rating, script.agg_scores
        )
    )

    corrections, stats = await CorrectionService.get_corrections(db, script_id)

    return AdjustedRatingResponse(
        original_rating=script.predicted_rating,
        adjusted_rating=adjusted_rating,
        original_scores=script.agg_scores,
        adjusted_scores=adjusted_scores,
        corrections_applied=len(corrections),
    )


@router.put("/{script_id}/content", response_model=ScriptResponse)
async def update_script_content(
    script_id: int, request: ScriptUpdateRequest, db: AsyncSession = Depends(get_db)
):
    script = await script_service.get_script(db, script_id)
    if not script:
        raise ScriptNotFoundError(script_id)

    updated_script = await CorrectionService.update_script_content(
        db, script_id, request.content
    )

    return updated_script


@router.post("/{script_id}/ai-suggest")
async def ai_suggest(
    script_id: int, request: AISuggestRequest, db: AsyncSession = Depends(get_db)
):
    script = await script_service.get_script(db, script_id)
    if not script:
        raise ScriptNotFoundError(script_id)

    async def generate_suggestion():
        try:
            result = await ml_client.what_if_analysis(
                request.content, request.instruction
            )

            suggested_text = result.get("modified_script", request.content)

            for i in range(0, len(suggested_text), 50):
                chunk = suggested_text[i : i + 50]
                yield chunk.encode("utf-8")
                await asyncio.sleep(0.05)

        except Exception as e:
            logger.error(f"AI suggestion error: {e}")
            yield b"Error: Unable to generate suggestion. Please try again."

    return StreamingResponse(generate_suggestion(), media_type="text/plain")
