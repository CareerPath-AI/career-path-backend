from fastapi import UploadFile, HTTPException
from PyPDF2 import PdfReader
from sqlalchemy.orm import Session
from app.utils.resume_analysis_utils import analyze_with_gemini
from app.models.user import User
from app.models.resume_analysis import ResumeAnalysis
from app.schemas.resume_analysis_schema import ResumeAnalysisResponse, ResumeAnalysisListResponse
from datetime import datetime, timezone
import io


class ResumeAnalysisService():
    async def analyze_resume_service(
        self, file: UploadFile, current_user: User, db: Session
    ) -> dict:
        """
        Service para análise de currículo
        """
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

        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        if not text.strip():
            raise ValueError("Nenhum texto foi encontrado no PDF")

        try:
            # Analisa o currículo com Gemini
            analysis_result = await analyze_with_gemini(text)

            # Salva no banco
            resume_analysis = ResumeAnalysis(
                user_id=current_user.id,
                original_filename=file.filename,
                analysis_result=analysis_result,
                created_at=datetime.now(timezone.utc)
            )

            db.add(resume_analysis)
            db.commit()
            db.refresh(resume_analysis)

            return ResumeAnalysisResponse(
                id = resume_analysis.id,
                original_filename=file.filename,
                analysis_result=analysis_result,
                created_at=resume_analysis.created_at
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Erro ao processar o currículo: {str(e)}"
            )
    
    async def get_resume_analysis_service(
        self, current_user: User, db: Session, skip: int, limit: int
    ):
        """
        Serviço para obter todas as análises de currículo do usuário
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
        
    async def get_resume_analysis_by_id_service(
        self, analysis_id: int, current_user: User, db: Session
    ):
        """
        Serviço para obter uma análise de currículo específica do usuário
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
            
            return analysis
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar análise: {str(e)}"
            )


resume_analysis_service = ResumeAnalysisService()
