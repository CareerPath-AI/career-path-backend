from fastapi import UploadFile, HTTPException
from app.utils.resume_analysis_utils import analyze_with_gemini
from app.models.user import User
from app.schemas.resume_analysis_schema import (
    ResumeAnalysisResponse, 
    ResumeAnalysisListResponse,
    ResumeAnalysisDeleteResponse
)
from app.utils.pdf_utils import check_pdf
from app.repository.resume_analysis_repository import ResumeAnalysisRepository
from datetime import datetime, timezone


class ResumeAnalysisService():
    def __init__(self, resume_analysis_repository: ResumeAnalysisRepository):
        self.resume_analysis_repository = resume_analysis_repository

    async def analyze_resume_service(
        self, file: UploadFile, current_user: User,
    ) -> ResumeAnalysisResponse:
        """
        Service para análise de currículo
        """
        text = await check_pdf(file)

        try:
            # Analisa o currículo com Gemini
            analysis_result = await analyze_with_gemini(text)

            # Salva no banco
            resume_analysis = await self.resume_analysis_repository.create(
                user_id=current_user.id,
                original_filename=file.filename,
                analysis_result=analysis_result,
                created_at=datetime.now(timezone.utc)
            )

            return ResumeAnalysisResponse(
                id=resume_analysis.id,
                original_filename=resume_analysis.original_filename,
                analysis_result=resume_analysis.analysis_result,
                created_at=resume_analysis.created_at
            )
        
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Erro ao processar o currículo: {str(e)}"
            )
    
    async def get_resume_analysis_service(
        self, current_user: User, skip: int, limit: int
    ):
        """
        Serviço para obter todas as análises de currículo do usuário
        """
        try:
            analyses, total_count = await self.resume_analysis_repository.get_by_user_id(
                user_id=current_user.id,
                skip=skip,
                limit=limit
            )

            if not analyses:
                raise HTTPException(
                    status_code=404, detail="Nenhuma análise de currículo encontrada"
                )

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
        self, analysis_id: int, current_user: User
    ) -> ResumeAnalysisResponse:
        """
        Serviço para obter uma análise de currículo específica do usuário
        """
        try:
            analysis = await self.resume_analysis_repository.get_by_id_and_user_id(
                analysis_id=analysis_id,
                user_id=current_user.id
            )

            if not analysis:
                raise HTTPException(
                    status_code=404,
                    detail="Análise não encontrada"
                )
            
            return ResumeAnalysisResponse(
                id=analysis.id,
                original_filename=analysis.original_filename,
                analysis_result=analysis.analysis_result,
                created_at=analysis.created_at
            )
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar análise: {str(e)}"
            )

    async def delete_resume_analysis_service(
            self, analysis_id: int, current_user: User
    ):
        """
        Serviço para deletar uma análise de currículo do usuário
        """
        try:
            analysis = await self.resume_analysis_repository.get_by_id_and_user_id(
                analysis_id=analysis_id,
                user_id=current_user.id
            )

            if not analysis:
                raise HTTPException(
                    status_code=404,
                    detail="Análise não encontrada"
                )
            
            await self.resume_analysis_repository.delete(analysis.id)

            return ResumeAnalysisDeleteResponse(
                message="Análise deletada com sucesso",
                deleted_id=analysis_id
            )
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao deletar análise: {str(e)}"
            )

