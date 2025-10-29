from fastapi import UploadFile, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.resume_analysis_utils import analyze_with_gemini
from app.models.user import User
from app.models.resume_analysis import ResumeAnalysis
from app.schemas.resume_analysis_schema import (
    ResumeAnalysisResponse, 
    ResumeAnalysisListResponse,
    ResumeAnalysisDeleteResponse
)
from app.utils.pdf_utils import check_pdf
from datetime import datetime, timezone


class ResumeAnalysisService():
    async def analyze_resume_service(
        self, file: UploadFile, current_user: User, db: AsyncSession
    ) -> dict:
        """
        Service para análise de currículo
        """
        text = await check_pdf(file)

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
            await db.commit()
            await db.refresh(resume_analysis)

            return ResumeAnalysisResponse(
                id = resume_analysis.id,
                original_filename=file.filename,
                analysis_result=analysis_result,
                created_at=resume_analysis.created_at
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Erro ao processar o currículo: {str(e)}"
            )
    
    async def get_resume_analysis_service(
        self, current_user: User, db: AsyncSession, skip: int, limit: int
    ):
        """
        Serviço para obter todas as análises de currículo do usuário
        """
        try:
            result = await db.execute(
                select(ResumeAnalysis)
                .where(ResumeAnalysis.user_id == current_user.id)
                .order_by(ResumeAnalysis.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            analyses = result.scalars().all()

            count_result = await db.execute(
                select(func.count(ResumeAnalysis.id))
                .where(ResumeAnalysis.user_id == current_user.id)
            )
            total_count = count_result.scalar_one()

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
        self, analysis_id: int, current_user: User, db: AsyncSession
    ):
        """
        Serviço para obter uma análise de currículo específica do usuário
        """
        try:
            result = await db.execute(
                select(ResumeAnalysis)
                .where(
                    ResumeAnalysis.id == analysis_id,
                    ResumeAnalysis.user_id == current_user.id
                )
            )
            analysis = result.scalar_one_or_none()

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
            self, analysis_id: int, current_user: User, db: AsyncSession
    ):
        """
        Serviço para deletar uma análise de currículo do usuário
        """
        try:
            result = await db.execute(
                select(ResumeAnalysis)
                .where(
                    ResumeAnalysis.id == analysis_id,
                    ResumeAnalysis.user_id == current_user.id
                )
            )
            analysis = result.scalar_one_or_none()

            if not analysis:
                raise HTTPException(
                    status_code=404,
                    detail="Análise não encontrada"
                )
            
            await db.delete(analysis)
            await db.commit()

            return ResumeAnalysisDeleteResponse(
                message="Análise deletada com sucesso",
                deleted_id=analysis_id
            )
        
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao deletar análise: {str(e)}"
            )


resume_analysis_service = ResumeAnalysisService()
