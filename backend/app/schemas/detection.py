from typing import Optional, Dict, List, Any
from pydantic import BaseModel
from datetime import datetime


class LineDetectionBase(BaseModel):
    line_start: int
    line_end: int
    detected_text: str
    context_before: Optional[str] = None
    context_after: Optional[str] = None
    category: str
    severity: float
    parents_guide_severity: Optional[str] = None
    character_name: Optional[str] = None
    page_number: Optional[int] = None
    matched_patterns: Optional[Dict[str, Any]] = None
    scene_id: Optional[int] = None


class LineDetectionCreate(LineDetectionBase):
    script_id: int


class LineDetectionResponse(LineDetectionBase):
    id: int
    script_id: int
    is_false_positive: bool
    user_corrected: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserCorrectionBase(BaseModel):
    correction_type: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    category: Optional[str] = None
    severity: Optional[float] = None
    note: Optional[str] = None


class UserCorrectionCreate(UserCorrectionBase):
    script_id: int
    detection_id: Optional[int] = None


class UserCorrectionResponse(UserCorrectionBase):
    id: int
    script_id: int
    detection_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ParentsGuideCategoryStats(BaseModel):
    severity: str
    episode_count: int
    percentage: float
    top_matches: int


class LineDetectionStatsResponse(BaseModel):
    total_detections: int
    by_category: Dict[str, int]
    total_matches: Dict[str, int]
    false_positives: int
    user_corrections: int
    parents_guide: Optional[Dict[str, ParentsGuideCategoryStats]] = None


class ScriptWithDetectionsResponse(BaseModel):
    script_id: int
    title: str
    predicted_rating: Optional[str]
    detections: List[LineDetectionResponse]
    stats: LineDetectionStatsResponse
    correction_count: int
