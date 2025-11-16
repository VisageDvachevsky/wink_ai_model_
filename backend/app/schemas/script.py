from pydantic import BaseModel, Field
from datetime import datetime


class ScriptCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=10)


class SceneResponse(BaseModel):
    id: int
    scene_id: int
    heading: str
    violence: float
    gore: float
    sex_act: float
    nudity: float
    profanity: float
    drugs: float
    child_risk: float
    weight: float
    sample_text: str | None

    class Config:
        from_attributes = True


class ScriptResponse(BaseModel):
    id: int
    title: str
    predicted_rating: str | None
    agg_scores: dict | None
    model_version: str | None
    total_scenes: int | None
    current_version: int | None = 1
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class ScriptDetailResponse(ScriptResponse):
    content: str
    scenes: list[SceneResponse] = []


class RatingJobResponse(BaseModel):
    job_id: str
    script_id: int
    status: str
    message: str


class RatingResultResponse(BaseModel):
    script_id: int
    predicted_rating: str
    reasons: list[str]
    agg_scores: dict
    top_trigger_scenes: list[SceneResponse]
    model_version: str
    total_scenes: int


class WhatIfRequest(BaseModel):
    script_id: int
    modification_request: str = Field(
        ..., min_length=3, description="What-if modification request"
    )


class WhatIfResponse(BaseModel):
    original_rating: str
    modified_rating: str
    original_scores: dict
    modified_scores: dict
    changes_applied: list[str]
    explanation: str
    rating_changed: bool


class LineFindingResponse(BaseModel):
    id: int
    line_start: int
    line_end: int
    category: str
    severity: float
    matched_text: str
    context_before: str | None
    context_after: str | None
    match_count: int
    rating_impact: str | None

    class Config:
        from_attributes = True


class LineFindingsSummaryResponse(BaseModel):
    total_findings: int
    by_category: dict
    findings: list[LineFindingResponse]


class CharacterAnalysisResponse(BaseModel):
    id: int
    character_name: str
    profanity_count: int
    violence_scenes: int
    sex_scenes: int
    drug_scenes: int
    total_problematic_scenes: int
    severity_score: float
    recommendations: dict | None
    scene_appearances: dict | None

    class Config:
        from_attributes = True


class CharacterAnalysisSummaryResponse(BaseModel):
    total_characters: int
    top_offenders: list[CharacterAnalysisResponse]
    all_characters: list[CharacterAnalysisResponse]


class ManualCorrectionCreate(BaseModel):
    finding_id: int | None = None
    scene_id: int | None = None
    correction_type: str = Field(..., pattern="^(false_positive|false_negative)$")
    category: str | None = None
    severity: float | None = None
    line_start: int | None = None
    line_end: int | None = None
    matched_text: str | None = None
    description: str | None = None


class ManualCorrectionResponse(BaseModel):
    id: int
    script_id: int
    finding_id: int | None
    scene_id: int | None
    correction_type: str
    category: str | None
    severity: float | None
    description: str | None
    line_start: int | None
    line_end: int | None
    matched_text: str | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CorrectionsSummaryResponse(BaseModel):
    corrections: list[ManualCorrectionResponse]
    stats: dict


class ScriptUpdateRequest(BaseModel):
    content: str = Field(..., min_length=10)


class AdjustedRatingResponse(BaseModel):
    original_rating: str
    adjusted_rating: str
    original_scores: dict
    adjusted_scores: dict
    corrections_applied: int


class AISuggestRequest(BaseModel):
    content: str = Field(..., min_length=10)
    instruction: str = Field(..., min_length=5, max_length=1000)
