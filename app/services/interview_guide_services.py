from fastapi import HTTPException, UploadFile
from app.models.user import User
from app.utils.interview_guide_utils import generate_interview_guide_with_gemini
from app.models.interview_guide import InterviewGuide
from app.schemas.interview_guide_schema import InterviewGuideResponse, InterviewGuideListResponse
from sqlalchemy.orm import Session
from PyPDF2 import PdfReader
import io


class InterviewGuideService:
    async def generate_interview_guide_service(self, file: UploadFile, job_description: str, current_user: User, db: Session) -> dict:
        """
        Service para geração de guia de entrevista
        """
        try:
            if not file.filename.lower().endswith(".pdf"):
                raise HTTPException(status_code=400, detail="O arquivo deve ser um PDF")

            # Lê o conteúdo do arquivo
            file_contents = await file.read()

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
                user_id=current_user.id,
                interview_guide=interview_guide_result
            )

            db.add(interview_guide)
            db.commit()
            db.refresh(interview_guide)

            return InterviewGuideResponse(
                id=interview_guide.id,
                interview_guide=interview_guide_result
            )

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Erro ao gerar guia de entrevista: {str(e)}"
            )
        
    async def get_interview_guide_service(self, current_user: User, db: Session, skip: int, limit: int) -> dict:
        """
        Serviço para obter guias de entrevista do usuário
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
        
    async def get_interview_guide_by_id_service(
        self, interview_guide_id: int, current_user: User, db: Session
    ):
        """
        Serviço para obter um guia de entrevista específico do usuário        
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


interview_guide_service = InterviewGuideService()
