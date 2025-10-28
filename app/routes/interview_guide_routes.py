from fastapi import APIRouter, UploadFile, File, Form, Depends, Query
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.models.user import User
from app.dependencies.security import verify_token
from app.services.interview_guide_services import interview_guide_service
from app.schemas.interview_guide_schema import InterviewGuideResponse, InterviewGuideListResponse, InterviewGuideDeleteResponse

interview_guide_router = APIRouter(prefix="/interview-guide", tags=["interview-guide"])


@interview_guide_router.post("/", response_model=InterviewGuideResponse)
async def generate_interview_guide(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Gera um roteiro detalhado para entrevista baseado no currículo e descrição da vaga
    """
    interview_guide = await interview_guide_service.generate_interview_guide_service(
        file, job_description, current_user, db
    )
    return interview_guide


@interview_guide_router.get("/", response_model=InterviewGuideListResponse)
async def get_my_interview_guides(
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de itens para pular"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de itens por página")
):
    """
    Retorna todos os interview_guides do usuário autenticado.
    """
    interview_guides = await interview_guide_service.get_interview_guide_service(
        current_user, db, skip, limit
    )
    return interview_guides


@interview_guide_router.get("/{interview_guide_id}", response_model=InterviewGuideResponse)
async def get_interview_guide(
    interview_guide_id: int,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Retorna um guia de entrevista específico do usuário.
    """
    interview_guide = await interview_guide_service.get_interview_guide_by_id_service(
        interview_guide_id, current_user, db
    )
    return interview_guide


@interview_guide_router.delete("/{interview_guide_id}", response_model=InterviewGuideDeleteResponse)
async def delete_interview_guide(
    interview_guide_id: int,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Deleta um guia de entrevista do usuário.
    """
    result = await interview_guide_service.delete_interview_guide_service(
        interview_guide_id, current_user, db
    )
    return result
