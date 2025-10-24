from fastapi import HTTPException
from app.models.user import User
from app.utils.interview_guide_utils import generate_interview_guide_with_gemini
from app.models.interview_guide import InterviewGuide
from sqlalchemy.orm import Session
from PyPDF2 import PdfReader
import io


async def generate_interview_guide_service(file_contents: bytes, filename: str, job_description: str, user: User, db: Session) -> dict:
    """
    Service para geração de guia de entrevista
    """
    try:
        # Lê e extrai texto do PDF
        if len(file_contents) == 0:
            raise ValueError("O arquivo está vazio")

        pdf_file = io.BytesIO(file_contents)
        reader = PdfReader(pdf_file)

        if reader.is_encrypted:
            raise ValueError("PDF criptografado não é suportado")

        resume_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                resume_text += page_text + "\n"

        if not resume_text.strip():
            raise ValueError("Nenhum texto foi encontrado no PDF")

        # Gera o guia de entrevista com Gemini
        interview_guide_result = await generate_interview_guide_with_gemini(resume_text, job_description)

        interview_guide = InterviewGuide(
            user_id=user.id,
            interview_guide=interview_guide_result
        )

        db.add(interview_guide)
        db.commit()
        db.refresh(interview_guide)

        return {
            "filename": filename,
            "job_description_preview": job_description[:100] + "..." if len(job_description) > 100 else job_description,
            "interview_guide": interview_guide_result
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro no serviço de IA: {str(e)}")
