from pydantic import BaseModel
from typing import Dict, Any, List


class InterviewGuideResponse(BaseModel):
    interview_guide: Dict[str, Any]

    class Config:
        from_attributes = True


class InterviewGuideListResponse(BaseModel):
    interview_guides: List[InterviewGuideResponse]
    total_count: int