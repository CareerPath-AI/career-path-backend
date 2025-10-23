from pydantic import BaseModel
from typing import Dict, Any


class ResumeAnalysisResponse(BaseModel):
    filename: str
    total_pages: int
    analysis: Dict[str, Any]
    analysis_id: int

    class Config:
        from_attributes = True
