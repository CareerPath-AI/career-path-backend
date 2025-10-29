from fastapi import Depends
from app.services.user_services import UserService
from app.services.resume_analysis_services import ResumeAnalysisService
from app.dependencies.repositories import get_user_repository, get_resume_analysis_repository
from app.repository.user_repository import UserRepository
from app.repository.resume_analysis_repository import ResumeAnalysisRepository


async def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(user_repository)

async def get_resume_analysis_service(
    resume_analysis_repository: ResumeAnalysisRepository = Depends(get_resume_analysis_repository)
) -> ResumeAnalysisService:
    return ResumeAnalysisService(resume_analysis_repository)

