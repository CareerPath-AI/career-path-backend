# app\routes\analyze_resume_routes.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from app.models.user import User
from app.services.resume_analysis_services import analyze_resume_service
from app.dependencies.security import verify_token

analyze_resume_router = APIRouter(prefix="/analyze-resume", tags=["resume-analysis"])


@analyze_resume_router.post("/")
async def analyze_resume(
    file: UploadFile = File(...), current_user: User = Depends(verify_token)
):
    """
    Faz análise do resumo enviado em .pdf e retorna para o usuário.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="O arquivo deve ser um PDF")

    try:
        # Lê o conteúdo do arquivo
        contents = await file.read()

        # Chama o service para processar a análise
        result = await analyze_resume_service(contents, file.filename)

        return JSONResponse(result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar o currículo: {str(e)}"
        )
