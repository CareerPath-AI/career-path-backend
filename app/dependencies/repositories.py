from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.user_repository import UserRepository
from app.repository.resume_analysis_repository import ResumeAnalysisRepository
from app.repository.interview_guide_repository import InterviewGuideRepository
from app.dependencies.database import get_db


async def get_user_repository(
    session: AsyncSession = Depends(get_db)
) -> UserRepository:
    return UserRepository(session)


async def get_resume_analysis_repository(
    session: AsyncSession = Depends(get_db)
) -> ResumeAnalysisRepository:
    return ResumeAnalysisRepository(session)


async def get_interview_guide_repository(
    session: AsyncSession = Depends(get_db)
) -> InterviewGuideRepository:
    return InterviewGuideRepository(session)
