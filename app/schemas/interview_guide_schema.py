from pydantic import BaseModel
from typing import Dict, Any


class InterviewGuideResponse(BaseModel):
    interview_guide: Dict[str, Any]