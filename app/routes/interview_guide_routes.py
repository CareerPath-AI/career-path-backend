from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Query
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.models.user import User
from app.models.interview_guide import InterviewGuide
from app.dependencies.security import verify_token
from app.services.interview_guide_services import generate_interview_guide_service
from app.schemas.interview_guide_schema import InterviewGuideResponse, InterviewGuideListResponse

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
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="O arquivo deve ser um PDF")

    try:
        # Lê o conteúdo do arquivo
        contents = await file.read()

        # Chama o service para processar o guia de entrevista
        interview_guide = await generate_interview_guide_service(
            contents, file.filename, job_description, current_user, db
        )

        return interview_guide

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao gerar guia de entrevista: {str(e)}"
        )


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
    try:
        interview_guides = db.query(InterviewGuide).filter(
            InterviewGuide.user_id == current_user.id
        ).order_by(
            InterviewGuide.created_at.desc()
        ).offset(skip).limit(limit).all()

        total_count = db.query(InterviewGuide).filter(
            InterviewGuide.user_id == current_user.id
        ).count()

        return InterviewGuideListResponse(
            interview_guides=interview_guides,
            total_count=total_count
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar análises: {str(e)}"
        )


@interview_guide_router.get("/{interview_guide_id}", response_model=InterviewGuideResponse)
async def get_interview_guide(
    interview_guide_id: int,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Retorna um guia de entrevista específico do usuário.
    """
    interview_guide = db.query(InterviewGuide).filter(
        InterviewGuide.id == interview_guide_id,
        InterviewGuide.user_id == current_user.id
    ).first()

    if not interview_guide:
        raise HTTPException(
            status_code=404,
            detail="Guia de entrevista não encontrado"
        )
    
    return interview_guide
