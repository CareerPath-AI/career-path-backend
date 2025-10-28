from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.resume_analysis import ResumeAnalysis
from app.services.resume_analysis_services import analyze_resume_service
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
    resume_analysis = await analyze_resume_service(file, current_user, db)
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
    try:
        analyses = db.query(ResumeAnalysis).filter(
            ResumeAnalysis.user_id == current_user.id
        ).order_by(
            ResumeAnalysis.created_at.desc()
        ).offset(skip).limit(limit).all()

        total_count = db.query(ResumeAnalysis).filter(
            ResumeAnalysis.user_id == current_user.id
        ).count()

        return ResumeAnalysisListResponse(
            analyses=analyses,
            total_count=total_count
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar análises: {str(e)}"
        )
    

@analyze_resume_router.get("/{analysis_id}", response_model=ResumeAnalysisResponse)
async def get_resume_analysis(
    analysis_id: int,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Retorna uma análise específica do usuário.
    """
    analysis = db.query(ResumeAnalysis).filter(
        ResumeAnalysis.id == analysis_id,
        ResumeAnalysis.user_id == current_user.id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Análise não encontrada"
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
    try:
        analysis = db.query(ResumeAnalysis).filter(
            ResumeAnalysis.id == analysis_id,
            ResumeAnalysis.user_id == current_user.id
        ).first()

        if not analysis:
            raise HTTPException(
                status_code=404,
                detail="Análise não encontrada"
            )
        
        db.delete(analysis)
        db.commit()

        return ResumeAnalysisDeleteResponse(
            message="Análise deletada com sucesso",
            deleted_id=analysis_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao deletar análise: {str(e)}"
        )
