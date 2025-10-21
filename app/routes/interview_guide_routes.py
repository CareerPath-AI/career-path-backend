from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.services.interview_guide_services import generate_interview_guide_service

interview_guide_router = APIRouter(prefix="/interview-guide", tags=["interview-guide"])

@interview_guide_router.post("/")
async def generate_interview_guide(
    file: UploadFile = File(...),
    job_description: str = Form(...)
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
        result = await generate_interview_guide_service(contents, file.filename, job_description)
        
        return JSONResponse(result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao gerar guia de entrevista: {str(e)}"
        )