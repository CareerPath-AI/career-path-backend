from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader
from app.services.analyze_services import analyze_with_gemini
import io

analyze_resume_router = APIRouter(prefix="/analyze-resume", tags=["analyze-resume"])


@analyze_resume_router.post("/")
async def analyze_resume(file: UploadFile = File(...)):
    """
    Faz análise do resumo enviado em .pdf e retorna para o usuário.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="O arquivo deve ser um PDF")

    try:
        # Lê e extrai texto do PDF
        contents = await file.read()

        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="O arquivo está vazio")

        pdf_file = io.BytesIO(contents)
        reader = PdfReader(pdf_file)

        if reader.is_encrypted:
            raise HTTPException(
                status_code=400, detail="PDF criptografado não é suportado"
            )

        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        if not text.strip():
            raise HTTPException(
                status_code=400, detail="Nenhum texto foi encontrado no PDF"
            )

        # Analisa o currículo com Gemini
        analysis_result = await analyze_with_gemini(text)

        return JSONResponse(
            {
                "filename": file.filename,
                "total_pages": len(reader.pages),
                "analysis": analysis_result,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar o currículo: {str(e)}"
        )
