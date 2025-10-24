from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime


class ResumeAnalysisResponse(BaseModel):
    id: int
    original_filename: str
    analysis_result: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeAnalysisListResponse(BaseModel):
    analyses: List[ResumeAnalysisResponse]
    total_count: int
