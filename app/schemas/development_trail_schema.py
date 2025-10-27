from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class DevelopmentTrailRequest(BaseModel):
    name: str = Field(..., example="Joao")
    age: Optional[int] = Field(None, example=23)
    education: Optional[str] = Field(None, example="Graduação em andamento")
    current_area: Optional[str] = Field(None, example="Estudante de TI")
    experience_in_years: Optional[int] = Field(None, example=1)
    skills: List[str] = Field(..., example=["Python", "SQL", "Git"])
    interested_technologies: Optional[List[str]] = Field(None, example=["Back-End", "Data Science"])
    current_level: Optional[str] = Field(None, example="Intermediário")
    professional_goal: str = Field(..., example="Desenvolvimento Back-End")
    available_time_week: Optional[str] = Field(None, example="Até 15 horas semanais")
    goal_timeframe: Optional[str] = Field(None, example="Conseguir estágio em até 6 meses")
    additional_information: Optional[str] = Field(None, example="Tenho interesse em DevOps e bancos de dados")


class DevelopmentTrailResponse(BaseModel):
    id: int
    development_trail: Dict[str, Any]

    class Config:
        from_attributes = True


class DevelopmentTrailListResponse(BaseModel):
    development_trails: List[DevelopmentTrailResponse]
    total_count: int


class DevelopmentTrailDeleteResponse(BaseModel):
    message: str
    deleted_id: int