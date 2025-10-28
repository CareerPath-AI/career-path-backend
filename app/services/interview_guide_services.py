from fastapi import HTTPException, UploadFile
from app.models.user import User
from app.utils.interview_guide_utils import generate_interview_guide_with_gemini
from app.models.interview_guide import InterviewGuide
from app.schemas.interview_guide_schema import (
    InterviewGuideResponse, 
    InterviewGuideListResponse,
    InterviewGuideDeleteResponse
)
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from PyPDF2 import PdfReader
import io


class InterviewGuideService:
    async def generate_interview_guide_service(self, file: UploadFile, job_description: str, current_user: User, db: AsyncSession) -> dict:
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
            await db.commit()
            await db.refresh(interview_guide)

            return InterviewGuideResponse(
                id=interview_guide.id,
                interview_guide=interview_guide_result
            )

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Erro ao gerar guia de entrevista: {str(e)}"
            )
        
    async def get_interview_guide_service(self, current_user: User, db: AsyncSession, skip: int, limit: int) -> dict:
        """
        Serviço para obter guias de entrevista do usuário
        """
        try:
            result = await db.execute(
                select(InterviewGuide)
                .where(InterviewGuide.user_id == current_user.id)
                .order_by(InterviewGuide.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            interview_guides = result.scalars().all()

            count_result = await db.execute(
                select(func.count(InterviewGuide.id))
                .where(InterviewGuide.user_id == current_user.id)
            )
            total_count = count_result.scalar_one()

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
        self, interview_guide_id: int, current_user: User, db: AsyncSession
    ):
        """
        Serviço para obter um guia de entrevista específico do usuário        
        """
        try:
            result = await db.execute(
                select(InterviewGuide)
                .where(
                    InterviewGuide.id == interview_guide_id,
                    InterviewGuide.user_id == current_user.id
                )
            )
            interview_guide = result.scalar_one_or_none()

            if not interview_guide:
                raise HTTPException(
                    status_code=404,
                    detail="Guia de entrevista não encontrado"
                )
            
            return interview_guide
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar guia de entrevista: {str(e)}"
            )
    
    async def delete_interview_guide_service(
        self, interview_guide_id: int, current_user: User, db: AsyncSession
    ):
        """
        Serviço para deletar um guia de entrevista do usuário
        """
        try:
            result = await db.execute(
                select(InterviewGuide)
                .where(
                    InterviewGuide.id == interview_guide_id,
                    InterviewGuide.user_id == current_user.id
                )
            )
            interview_guide = result.scalar_one_or_none()

            if not interview_guide:
                raise HTTPException(
                    status_code=404,
                    detail="Guia de entrevista não encontrado"
                )
            
            await db.delete(interview_guide)
            await db.commit()

            return InterviewGuideDeleteResponse(
                message="Guia de entrevista deletado com sucesso",
                deleted_id=interview_guide_id
            )
        
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao deletar guia de entrevista: {str(e)}"
            )


interview_guide_service = InterviewGuideService()
