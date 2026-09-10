from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.enums import Verdict


class AnalysisResultBase(BaseModel):
    risk_score: float = 0.0
    verdict: Verdict = Verdict.UNKNOWN
    detection_reasons: Optional[str] = None
    analysis_duration_ms: Optional[float] = None
    details_json: Optional[str] = None


class AnalysisResultCreate(AnalysisResultBase):
    email_id: str


class AnalysisResultResponse(AnalysisResultBase):
    id: str
    email_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
