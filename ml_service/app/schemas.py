from pydantic import BaseModel, Field


class ScriptRequest(BaseModel):
    script_id: str | None = None
    text: str = Field(..., min_length=10, description="Full movie script text")


class SceneRecommendation(BaseModel):
    scene_id: int
    heading: str
    recommendations: list[str]


class SceneFeatures(BaseModel):
    scene_id: int
    heading: str
    violence: float = Field(ge=0, le=1)
    gore: float = Field(ge=0, le=1)
    sex_act: float = Field(ge=0, le=1)
    nudity: float = Field(ge=0, le=1)
    profanity: float = Field(ge=0, le=1)
    drugs: float = Field(ge=0, le=1)
    child_risk: float = Field(ge=0, le=1)
    weight: float
    sample_text: str | None = None
    recommendations: list[str] = Field(default_factory=list)


class ScriptRatingResponse(BaseModel):
    script_id: str | None
    predicted_rating: str = Field(..., pattern="^(0\\+|6\\+|12\\+|16\\+|18\\+)$")
    reasons: list[str]
    agg_scores: dict[str, float]
    top_trigger_scenes: list[SceneFeatures]
    model_version: str
    total_scenes: int
    evidence_excerpts: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
    model_version: str
    model_loaded: bool


class WhatIfRequest(BaseModel):
    script_text: str = Field(..., min_length=10, description="Original script text")
    modification_request: str = Field(
        ...,
        min_length=3,
        description="What-if modification request (e.g., 'remove scene 12-13', 'replace fight with verbal conflict')",
    )


class WhatIfResponse(BaseModel):
    original_rating: str
    modified_rating: str
    original_scores: dict[str, float]
    modified_scores: dict[str, float]
    changes_applied: list[str]
    explanation: str
    rating_changed: bool


class EntityTargetSchema(BaseModel):
    entity_type: str = "all"
    entity_names: list[str] | None = None


class ModificationConfigSchema(BaseModel):
    type: str = Field(..., description="Type of modification")
    params: dict = Field(default_factory=dict)
    targets: EntityTargetSchema | None = None
    scope: list[int] | None = None


class StructuredWhatIfRequest(BaseModel):
    script_text: str = Field(..., min_length=10)
    modifications: list[ModificationConfigSchema]
    use_llm: bool = False
    llm_provider: str | None = None
    preserve_structure: bool = True


class EntityInfoSchema(BaseModel):
    type: str
    name: str
    mentions: int
    scenes: list[int]


class SceneInfoSchema(BaseModel):
    scene_id: int
    scene_type: str
    characters: list[str]
    location: str | None
    summary: str | None


class AdvancedWhatIfResponse(BaseModel):
    original_rating: str
    modified_rating: str
    original_scores: dict[str, float]
    modified_scores: dict[str, float]
    modifications_applied: list[dict]
    entities_extracted: list[EntityInfoSchema]
    scene_analysis: list[SceneInfoSchema]
    explanation: str
    modified_script: str | None = None
    rating_changed: bool


class RatingAdvisorRequest(BaseModel):
    script_text: str = Field(..., min_length=10)
    current_rating: str | None = None
    target_rating: str = Field(..., pattern="^(0\\+|6\\+|12\\+|16\\+|18\\+)$")
    language: str = "en"
    include_rewrites: bool = False


class RecommendationActionSchema(BaseModel):
    action_type: str
    scene_id: int
    description: str
    impact_score: float
    category: str
    specific_changes: list[str]
    difficulty: str


class SceneIssueSchema(BaseModel):
    scene_id: int
    scene_number: int
    content_preview: str
    issues: dict[str, float]
    severity: str
    recommendations: list[str]


class RatingGapSchema(BaseModel):
    dimension: str
    current_score: float
    target_score: float
    gap: float
    priority: str


class RatingAdvisorResponse(BaseModel):
    current_rating: str
    target_rating: str
    is_achievable: bool
    confidence: float
    current_scores: dict[str, float]
    target_scores: dict[str, float]
    rating_gaps: list[RatingGapSchema]
    problematic_scenes: list[SceneIssueSchema]
    recommended_actions: list[RecommendationActionSchema]
    summary: str
    estimated_effort: str
    alternative_targets: list[str] | None = None


class SmartSuggestionSchema(BaseModel):
    text: str = Field(..., description="Suggestion text")
    category: str = Field(..., description="Category (violence, profanity, etc)")
    icon: str = Field(..., description="Emoji icon")
    priority: int = Field(..., ge=1, le=10, description="Priority 1-10")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    affected_scenes: list[int] = Field(default_factory=list)
    reasoning: str = Field(..., description="Why this suggestion")


class SmartSuggestionsRequest(BaseModel):
    script_text: str = Field(..., min_length=10)
    current_scores: dict[str, float] | None = None
    current_rating: str | None = None
    language: str = "ru"
    max_suggestions: int = Field(default=8, ge=1, le=20)


class SmartSuggestionsResponse(BaseModel):
    suggestions: list[SmartSuggestionSchema]
    analysis_summary: str
    current_rating: str
    total_scenes: int


class LineIssueContext(BaseModel):
    line: int
    text: str


class LineIssueSchema(BaseModel):
    line_number: int
    line_text: str
    category: str
    matched_words: list[str]
    match_count: int
    context_before: list[LineIssueContext]
    context_after: list[LineIssueContext]
    severity: float


class LineDetectionRequest(BaseModel):
    text: str = Field(..., min_length=1)
    context_lines: int = Field(default=3, ge=0, le=10)


class LineDetectionResponse(BaseModel):
    total_issues: int
    issues: list[LineIssueSchema]
    statistics: dict[str, int]
    summary: dict[str, Any]


class ManualCorrectionSchema(BaseModel):
    issue_id: str
    correction_type: str = Field(..., pattern="^(false_positive|false_negative)$")
    category: str
    line_number: int
    notes: str | None = None


class ScriptCorrectionRequest(BaseModel):
    script_id: int
    corrections: list[ManualCorrectionSchema]


class ScriptEditRequest(BaseModel):
    script_id: int
    content: str = Field(..., min_length=10)
    edit_description: str | None = None


class VersionSchema(BaseModel):
    version_id: str
    script_id: int
    content: str
    rating: str | None
    created_at: str
    description: str | None
    author: str = "user"


class VersionListResponse(BaseModel):
    script_id: int
    versions: list[VersionSchema]
    current_version: str
