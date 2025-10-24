from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.models.user import User
from app.dependencies.security import verify_token
from app.services.interview_guide_services import generate_interview_guide_service
from app.schemas.interview_guide_schema import InterviewGuideResponse

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
