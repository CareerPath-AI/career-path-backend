from fastapi import Depends
from app.services.user_services import UserService
from app.services.resume_analysis_services import ResumeAnalysisService
from app.services.interview_guide_services import InterviewGuideService
from app.dependencies.repositories import get_user_repository, get_resume_analysis_repository, get_interview_guide_repository
from app.repository.user_repository import UserRepository
from app.repository.resume_analysis_repository import ResumeAnalysisRepository
from app.repository.interview_guide_repository import InterviewGuideRepository


async def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(user_repository)

async def get_resume_analysis_service(
    resume_analysis_repository: ResumeAnalysisRepository = Depends(get_resume_analysis_repository)
) -> ResumeAnalysisService:
    return ResumeAnalysisService(resume_analysis_repository)

async def get_interview_guide_service(
    interview_guide_repository: InterviewGuideRepository = Depends(get_interview_guide_repository)
) -> InterviewGuideService:
    return InterviewGuideService(interview_guide_repository)
