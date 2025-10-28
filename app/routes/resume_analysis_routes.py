from fastapi import APIRouter, UploadFile, File, Depends, Query
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.resume_analysis_services import resume_analysis_service
from app.dependencies.security import verify_token
from app.dependencies.database import get_db
from app.schemas.resume_analysis_schema import ResumeAnalysisResponse, ResumeAnalysisListResponse, ResumeAnalysisDeleteResponse

analyze_resume_router = APIRouter(prefix="/analyze-resume", tags=["resume-analysis"])


@analyze_resume_router.post("/", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """
    Faz análise do resumo enviado em .pdf e retorna para o usuário.
    """
    resume_analysis = await resume_analysis_service.analyze_resume_service(
        file, current_user, db
    )
    return resume_analysis


@analyze_resume_router.get("/", response_model=ResumeAnalysisListResponse)
async def get_my_resume_analyses(
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de itens para pular"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de itens por página")
):
    """
    Retorna todas as análises de currículo do usuário autenticado.
    """
    analyses = await resume_analysis_service.get_resume_analysis_service(
        current_user, db, skip, limit
    )
    return analyses
    

@analyze_resume_router.get("/{analysis_id}", response_model=ResumeAnalysisResponse)
async def get_resume_analysis(
    analysis_id: int,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Retorna uma análise específica do usuário.
    """
    analysis = await resume_analysis_service.get_resume_analysis_by_id_service(
        analysis_id, current_user, db
    )
    return analysis


@analyze_resume_router.delete("/{analysis_id}", response_model=ResumeAnalysisDeleteResponse)
async def delete_resume_analysis(
    analysis_id: int,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Delete uma análise de currículo do usuário.
    """
    result = await resume_analysis_service.delete_resume_analysis_service(
        analysis_id, current_user, db
    )
    return result
